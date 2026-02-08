from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)
from sqlalchemy import or_
from . import db
from .models import User, BusinessProfile, Service, Order, Message
from .forms import (
    RegisterForm,
    LoginForm,
    ProfileForm,
    ServiceForm,
    MessageForm,
    OrderStatusForm,
)
from .utils import admin_required

main_bp = Blueprint("main", __name__)


@main_bp.context_processor
def inject_globals():
    return dict(Order=Order)


@main_bp.route("/")
def index():
    # Show latest services
    services = Service.query.order_by(Service.created_at.desc()).limit(8).all()
    return render_template("index.html", services=services)


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("Email is already registered.", "warning")
            return redirect(url_for("main.register"))

        user = User(email=form.email.data.lower().strip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # Get user.id

        profile = BusinessProfile(
            company_name=form.company_name.data.strip(),
            user_id=user.id,
            contact_email=user.email,
        )
        db.session.add(profile)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    profile = current_user.profile
    my_services = current_user.services.order_by(Service.created_at.desc()).all()
    orders_buyer = current_user.orders_as_buyer.order_by(Order.created_at.desc()).all()
    orders_seller = current_user.orders_as_seller.order_by(Order.created_at.desc()).all()
    return render_template(
        "dashboard.html",
        profile=profile,
        my_services=my_services,
        orders_buyer=orders_buyer,
        orders_seller=orders_seller,
    )


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile = current_user.profile
    if not profile:
        profile = BusinessProfile(user_id=current_user.id, company_name="")
        db.session.add(profile)
        db.session.commit()

    form = ProfileForm(
        company_name=profile.company_name,
        description=profile.description,
        website=profile.website,
        location=profile.location,
        phone=profile.phone,
        contact_email=profile.contact_email,
    )

    if form.validate_on_submit():
        profile.company_name = form.company_name.data
        profile.description = form.description.data
        profile.website = form.website.data
        profile.location = form.location.data
        profile.phone = form.phone.data
        profile.contact_email = form.contact_email.data
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("main.profile"))

    return render_template("profile.html", form=form)


@main_bp.route("/services")
def service_list():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    services_query = Service.query

    if q:
        like_q = f"%{q}%"
        services_query = services_query.filter(
            or_(Service.title.ilike(like_q), Service.description.ilike(like_q))
        )
    if category:
        services_query = services_query.filter(Service.category.ilike(f"%{category}%"))

    services = services_query.order_by(Service.created_at.desc()).all()
    return render_template("service_list.html", services=services, q=q, category=category)


@main_bp.route("/service/<int:service_id>", methods=["GET", "POST"])
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    can_request = current_user.is_authenticated and current_user.id != service.owner_id

    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("You must be logged in to request a service.", "warning")
            return redirect(url_for("main.login"))
        if current_user.id == service.owner_id:
            flash("You cannot order your own service.", "warning")
            return redirect(url_for("main.service_detail", service_id=service.id))

        order = Order(
            service_id=service.id,
            buyer_id=current_user.id,
            seller_id=service.owner_id,
        )
        db.session.add(order)
        db.session.commit()
        flash("Service requested. You can now chat with the seller.", "success")
        return redirect(url_for("main.order_detail", order_id=order.id))

    return render_template("service_detail.html", service=service, can_request=can_request)


@main_bp.route("/service/create", methods=["GET", "POST"])
@login_required
def create_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            title=form.title.data,
            category=form.category.data,
            description=form.description.data,
            price=form.price.data,
            delivery_time=form.delivery_time.data,
            tags=form.tags.data,
            owner_id=current_user.id,
        )
        db.session.add(service)
        db.session.commit()
        flash("Service created successfully.", "success")
        return redirect(url_for("main.service_detail", service_id=service.id))
    return render_template("create_service.html", form=form)


@main_bp.route("/service/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service.owner_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = ServiceForm(
        title=service.title,
        category=service.category,
        description=service.description,
        price=service.price,
        delivery_time=service.delivery_time,
        tags=service.tags,
    )

    if form.validate_on_submit():
        service.title = form.title.data
        service.category = form.category.data
        service.description = form.description.data
        service.price = form.price.data
        service.delivery_time = form.delivery_time.data
        service.tags = form.tags.data
        db.session.commit()
        flash("Service updated.", "success")
        return redirect(url_for("main.service_detail", service_id=service.id))

    return render_template("create_service.html", form=form, edit_mode=True)


@main_bp.route("/orders")
@login_required
def orders():
    orders_buyer = current_user.orders_as_buyer.order_by(Order.created_at.desc()).all()
    orders_seller = current_user.orders_as_seller.order_by(Order.created_at.desc()).all()
    return render_template(
        "orders.html",
        orders_buyer=orders_buyer,
        orders_seller=orders_seller,
    )


@main_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.id not in (order.buyer_id, order.seller_id) and not current_user.is_admin:
        abort(403)

    message_form = MessageForm()
    status_form = None

    is_seller = current_user.id == order.seller_id
    if is_seller or current_user.is_admin:
        status_form = OrderStatusForm(status=order.status)
        if status_form.validate_on_submit() and "status" in request.form:
            order.status = status_form.status.data
            db.session.commit()
            flash("Order status updated.", "success")
            return redirect(url_for("main.order_detail", order_id=order.id))

    if message_form.validate_on_submit() and "content" in request.form:
        msg = Message(
            content=message_form.content.data,
            order_id=order.id,
            sender_id=current_user.id,
        )
        db.session.add(msg)
        db.session.commit()
        flash("Message sent.", "success")
        return redirect(url_for("main.order_detail", order_id=order.id))

    messages = order.messages.order_by(Message.created_at.asc()).all()
    return render_template(
        "messages.html",
        order=order,
        messages=messages,
        message_form=message_form,
        status_form=status_form,
    )


@main_bp.route("/messages")
@login_required
def messages_overview():
    # Show last message per order the user is part of
    orders = (
        Order.query.filter(
            (Order.buyer_id == current_user.id) | (Order.seller_id == current_user.id)
        )
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("messages.html", overview_orders=orders)


@main_bp.route("/admin")
@login_required
@admin_required
def admin_panel():
    users = User.query.order_by(User.created_at.desc()).all()
    services = Service.query.order_by(Service.created_at.desc()).all()
    return render_template("dashboard.html", admin_mode=True, users=users, services=services)


@main_bp.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    if current_user.id == user_id:
        flash("You cannot delete your own admin account.", "warning")
        return redirect(url_for("main.admin_panel"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "success")
    return redirect(url_for("main.admin_panel"))


@main_bp.route("/admin/delete_service/<int:service_id>", methods=["POST"])
@login_required
@admin_required
def admin_delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash("Service deleted.", "success")
    return redirect(url_for("main.admin_panel"))
