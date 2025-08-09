from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from .storage import UserStorage
import os
from datetime import datetime
import uuid
import glob
from flask import send_from_directory

bp = Blueprint('main', __name__)

# صفحه اصلی
@bp.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

# ثبت نام
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # بررسی وجود کاربر
        if os.path.exists(f'users/{username}'):
            flash('این نام کاربری قبلا ثبت شده است', 'error')
            return redirect(url_for('main.register'))

        # ایجاد پوشه کاربر
        os.makedirs(f'users/{username}')

        # ذخیره اطلاعات کاربر
        storage = UserStorage(username)
        storage.update_profile({
            'username': username,
            'password': generate_password_hash(password),
            'joined_at': datetime.now().isoformat(),
            'liked_notes': []
        })

        session['username'] = username
        flash('ثبت نام با موفقیت انجام شد', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')

# ورود به سیستم
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not os.path.exists(f'users/{username}'):
            flash('نام کاربری یا رمز عبور اشتباه است', 'error')
            return redirect(url_for('main.login'))

        storage = UserStorage(username)
        profile = storage.get_profile()

        if not check_password_hash(profile['password'], password):
            flash('نام کاربری یا رمز عبور اشتباه است', 'error')
            return redirect(url_for('main.login'))

        session['username'] = username
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

# خروج
@bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.login'))

# داشبورد کاربر
@bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    username = session['username']
    storage = UserStorage(username)
    notes = storage.get_notes()

    return render_template('dashboard.html',
                         username=username,
                         notes=reversed(notes))

# افزودن یادداشت جدید
@bp.route('/add_note', methods=['POST'])
def add_note():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    username = session['username']
    content = request.form['content']

    if not content.strip():
        flash('متن یادداشت نمی‌تواند خالی باشد', 'error')
        return redirect(url_for('main.dashboard'))

    storage = UserStorage(username)
    storage.add_note({
        'content': content,
        'public': False  # یادداشت‌ها به صورت خصوصی هستند
    })

    flash('یادداشت با موفقیت ذخیره شد', 'success')
    return redirect(url_for('main.dashboard'))

# مدیریت لایک‌ها
@bp.route('/like/<note_id>')
def toggle_like(note_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    username = session['username']
    storage = UserStorage(username)

    # دریافت یادداشت
    note = storage.get_note(note_id)
    if not note:
        flash('یادداشت مورد نظر یافت نشد', 'error')
        return redirect(url_for('main.dashboard'))

    # بررسی لایک قبلی
    profile = storage.get_profile()
    if note_id in profile['liked_notes']:
        # حذف لایک
        note['likes'].remove(username)
        profile['liked_notes'].remove(note_id)
    else:
        # افزودن لایک
        note['likes'].append(username)
        profile['liked_notes'].append(note_id)

    # ذخیره تغییرات
    storage.update_note(note_id, note)
    storage.update_profile(profile)

    return redirect(url_for('main.dashboard'))

# افزودن کامنت
@bp.route('/comment/<note_id>', methods=['POST'])
def add_comment(note_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    username = session['username']
    comment_text = request.form['comment']

    if not comment_text.strip():
        flash('متن نظر نمی‌تواند خالی باشد', 'error')
        return redirect(url_for('main.dashboard'))

    storage = UserStorage(username)
    note = storage.get_note(note_id)

    if not note:
        flash('یادداشت مورد نظر یافت نشد', 'error')
        return redirect(url_for('main.dashboard'))

    storage.add_comment(note_id, {
        'author': username,
        'text': comment_text,
        'created_at': datetime.now().isoformat()
    })

    flash('نظر شما با موفقیت ثبت شد', 'success')
    return redirect(url_for('main.dashboard'))

# مشاهده لیست کاربران
@bp.route('/users')
def list_users():
    user_dirs = [os.path.basename(u) for u in glob.glob('users/*') if os.path.isdir(u)]
    return render_template('users.html', users=user_dirs)

# مشاهده پروفایل کاربر
@bp.route('/profile/<username>', methods=['GET'])
def view_profile(username):
    if not os.path.exists(f'users/{username}/profile.json'):
        abort(404)
    storage = UserStorage(username)
    profile = storage.get_profile()
    notes = storage.get_notes()
    is_self = ('username' in session and session['username'] == username)
    current_user = session.get('username')
    return render_template('profile.html', profile=profile, username=username, is_self=is_self, current_user=current_user, notes=notes)

# لایک/آنلایک پروفایل
@bp.route('/profile/<username>/like', methods=['POST'])
def like_profile(username):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    if not os.path.exists(f'users/{username}/profile.json'):
        abort(404)
    storage = UserStorage(username)
    liker = session['username']
    profile = storage.get_profile()
    if liker in profile.get('profile_likes', []):
        storage.unlike_profile(liker)
    else:
        storage.like_profile(liker)
    return redirect(url_for('main.view_profile', username=username))

# افزودن کامنت به پروفایل
@bp.route('/profile/<username>/comment', methods=['POST'])
def comment_profile(username):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    if not os.path.exists(f'users/{username}/profile.json'):
        abort(404)
    text = request.form.get('comment', '').strip()
    if not text:
        flash('متن نظر نمی‌تواند خالی باشد', 'error')
        return redirect(url_for('main.view_profile', username=username))
    storage = UserStorage(username)
    storage.add_profile_comment(session['username'], text)
    flash('نظر شما با موفقیت ثبت شد', 'success')
    return redirect(url_for('main.view_profile', username=username))

@bp.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    username = session['username']
    # حذف پوشه کاربر
    UserStorage.delete_user(username)
    session.pop('username', None)
    flash('اکانت شما با موفقیت حذف شد.', 'success')
    return redirect(url_for('main.login'))
