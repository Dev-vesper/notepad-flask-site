import json
import os
from datetime import datetime
from pathlib import Path
import shutil

class UserStorage:
    def __init__(self, username, create_if_missing=True):
        self.username = username
        self.user_folder = Path(f"users/{username}")
        self.notes_file = self.user_folder / "notes.json"
        self.profile_file = self.user_folder / "profile.json"

        if create_if_missing:
            self.user_folder.mkdir(parents=True, exist_ok=True)
            self._init_files()

    def _init_files(self):
        """ایجاد فایل‌های اولیه اگر وجود ندارند"""
        if not self.notes_file.exists():
            with open(self.notes_file, 'w') as f:
                json.dump([], f)

        if not self.profile_file.exists():
            with open(self.profile_file, 'w') as f:
                json.dump({
                    "username": self.username,
                    "joined_at": datetime.now().isoformat(),
                    "liked_notes": [],
                    "profile_likes": [],  # کاربران لایک‌کننده پروفایل
                    "profile_comments": []  # کامنت‌های پروفایل
                }, f)

    # --- متدهای مدیریت پروفایل ---
    def get_profile(self):
        """دریافت اطلاعات پروفایل کاربر"""
        with open(self.profile_file, 'r') as f:
            return json.load(f)

    def update_profile(self, profile_data):
        """ذخیره اطلاعات پروفایل کاربر"""
        # مطمئن شوید فیلدهای ضروری وجود دارند
        required_fields = ['username', 'password', 'joined_at', 'liked_notes', 'profile_likes', 'profile_comments']
        for field in required_fields:
            if field not in profile_data:
                if field in ['liked_notes', 'profile_likes', 'profile_comments']:
                    profile_data[field] = []
                else:
                    profile_data[field] = ''  # یا مقدار پیش‌فرض مناسب

        with open(self.profile_file, 'w') as f:
            json.dump(profile_data, f, indent=4)

    # --- متدهای لایک و کامنت پروفایل ---
    def like_profile(self, liker_username):
        profile = self.get_profile()
        if liker_username not in profile.get('profile_likes', []):
            profile.setdefault('profile_likes', []).append(liker_username)
            self.update_profile(profile)

    def unlike_profile(self, liker_username):
        profile = self.get_profile()
        if liker_username in profile.get('profile_likes', []):
            profile['profile_likes'].remove(liker_username)
            self.update_profile(profile)

    def add_profile_comment(self, author, text):
        profile = self.get_profile()
        comment = {
            'author': author,
            'text': text,
            'created_at': datetime.now().isoformat()
        }
        profile.setdefault('profile_comments', []).append(comment)
        self.update_profile(profile)

    # --- متدهای مدیریت یادداشت‌ها ---
    def get_notes(self):
        """دریافت تمام یادداشت‌های کاربر"""
        with open(self.notes_file, 'r') as f:
            return json.load(f)

    def get_note(self, note_id):
        """دریافت یک یادداشت خاص"""
        notes = self.get_notes()
        for note in notes:
            if str(note.get('id')) == str(note_id):
                return note
        return None

    def add_note(self, note_data):
        """افزودن یادداشت جدید"""
        notes = self.get_notes()
        note = {
            "id": len(notes) + 1,
            **note_data,
            "created_at": datetime.now().isoformat(),
            "likes": [],
            "comments": []
        }
        notes.append(note)
        self._save_notes(notes)
        return note

    def update_note(self, note_id, note_data):
        """به‌روزرسانی یک یادداشت"""
        notes = self.get_notes()
        for i, note in enumerate(notes):
            if str(note.get('id')) == str(note_id):
                notes[i] = {**note, **note_data}
                self._save_notes(notes)
                return notes[i]
        return None

    def _save_notes(self, notes):
        """ذخیره لیست یادداشت‌ها"""
        with open(self.notes_file, 'w') as f:
            json.dump(notes, f, indent=4)

    # --- متدهای مدیریت کامنت‌ها ---
    def add_comment(self, note_id, comment_data):
        """افزودن کامنت به یک یادداشت"""
        notes = self.get_notes()
        for note in notes:
            if str(note.get('id')) == str(note_id):
                comment = {
                    "id": len(note.get('comments', [])) + 1,
                    **comment_data,
                    "created_at": datetime.now().isoformat()
                }
                note['comments'].append(comment)
                self._save_notes(notes)
                return comment
        return None

    @staticmethod
    def delete_user(username):
        user_folder = Path(f"users/{username}")
        if user_folder.exists() and user_folder.is_dir():
            shutil.rmtree(user_folder)
