from django.shortcuts import redirect, render
from userauths.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.translation import gettext as _
from userauths.models import User
from utils.email_service import send_activation_email, is_valid_email
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.mail import BadHeaderError
import logging
from userauths.models import User,Profile
from django.contrib.auth.decorators import login_required

from core.forms import *
import shortuuid
from core.models import Image 

logger = logging.getLogger(__name__)

def register_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, _("Bạn đã được đăng xuất để đăng ký tài khoản mới."))
        return redirect('userauths:sign-up')

    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            role = form.cleaned_data.get("role")

            if not is_valid_email(email):
                messages.error(request, _("Email không hợp lệ hoặc không tồn tại."))
                return redirect('userauths:sign-up')
            new_user = form.save(commit=False)
            new_user.is_active = False
            new_user.save()
            
            # Nếu là vendor thì chuyển sang trang nhập vendor info
            if role == "vendor":
                request.session["pending_vendor_user_id"] = new_user.id
                return redirect("userauths:vendor-register")
            
            # Nếu là customer thì gửi mail luôn
            username = form.cleaned_data.get("username")
            #Tao token va uidb64
            uidb64 = urlsafe_base64_encode(force_bytes(new_user.pk))
            token = default_token_generator.make_token(new_user)
            try:
                send_activation_email(email, username, uidb64, token)
            except BadHeaderError:
                logger.error(f"Lỗi header khi gửi mail tới {email}")
                messages.error(request, _("Có lỗi khi gửi email kích hoạt."))
                return redirect("userauths:sign-up")
            except Exception as e:
                logger.error(f"Gửi mail kích hoạt thất bại: {e}")
                messages.error(request, _("Không thể gửi email kích hoạt. Vui lòng thử lại sau."))
                return redirect("userauths:sign-up")
            #send_welcome_email(email, username)
            context = {
                "username": username,
                "email": email
            }
            return render(request, "userauths/activation_pending.html", context)
    else:
        form = UserRegisterForm()
    return render(request, "userauths/sign-up.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, _("You are already logged in."))
        if request.user.role == "vendor":
            return redirect("useradmin:dashboard")
        else:
            return redirect("core:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, email=user_obj.email, password=password)
            if user is not None:
                #check vendor_active
                if user.role == "vendor":
                    try:
                        vendor = Vendor.objects.get(user=user)
                        if not vendor.vendor_active:
                            messages.warning(request, _("Vui lòng chờ admin phê duyệt tài khoản của bạn."))
                            return redirect("userauths:sign-in")
                    except Vendor.DoesNotExist:
                        messages.warning(request, _("Bạn chưa đăng ký thông tin cửa hàng."))
                        return redirect("userauths:sign-in")
                
                login(request, user)
                messages.success(request, _("Login successfully!"))
                if user.role == "vendor":
                    return redirect("useradmin:dashboard")
                else:
                    return redirect("core:index")
            else:
                messages.warning(request, _("User does not exist. Create an account."))
        except:
            messages.warning(request, f"User with {email} does not exists")

    context = {}

    return render(request, "userauths/sign-in.html", context)

def logout_view(request):
    logout(request)
    messages.success(request, "You logged out.")
    return redirect("userauths:sign-in")


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        logout(request)
        user.is_active = True
        user.save()
        messages.success(request, "Tài khoản đã được kích hoạt, bạn có thể đăng nhập.")
        return redirect("userauths:sign-in")
    else:
        messages.error(request, "Liên kết kích hoạt không hợp lệ hoặc đã hết hạn.")
        return redirect("core:index")

@login_required
def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile Updated Successfully.")
            return redirect("core:dashboard")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "userauths/profile-edit.html", context)

        
        
def vendor_register_view(request):
    user_id = request.session.get("pending_vendor_user_id")
    if not user_id:
        messages.error(request, _("Không tìm thấy tài khoản cần đăng ký Vendor."))
        return redirect("userauths:sign-up")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = VendorRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = user
            vendor.vendor_active = False
            vendor.vid = f"v-{shortuuid.uuid()[:10]}"
            vendor.save()

            # Nếu có upload logo
            image = form.cleaned_data.get("image")
            if image:
                Image.objects.create(
                    image=image,
                    alt_text=vendor.title,
                    object_type="vendor",
                    object_id=vendor.vid,
                    is_primary=True
                )

            # Gửi mail xác thực user
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            try:
                send_activation_email(user.email, user.username, uidb64, token)
            except Exception as e:
                logger.error(f"Gửi mail kích hoạt thất bại: {e}")
                messages.error(request, _("Không thể gửi email kích hoạt."))
                return redirect("userauths:sign-up")

            del request.session["pending_vendor_user_id"]
            return render(request, "userauths/activation_pending.html", {"username": user.username, "email": user.email})
    else:
        form = VendorRegisterForm()

    return render(request, "userauths/vendor-register.html", {"form": form})

