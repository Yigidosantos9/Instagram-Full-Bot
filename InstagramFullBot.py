from instagrapi import Client
import os
import moviepy.editor as mp
from PIL import Image
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, MULTIPLE
from datetime import datetime, timedelta
import threading
import time
from send2trash import send2trash

# Login function
def login(username, password):
    cl = Client()
    cl.login(username, password)
    return cl

# Instagram actions
def follow_users(cl, usernames):
    for username in usernames:
        user_id = cl.user_id_from_username(username)
        cl.user_follow(user_id)

def like_posts(cl, post_urls):
    for post_url in post_urls:
        media_id = cl.media_pk_from_url(post_url)
        cl.media_like(media_id)

def comment_on_posts(cl, post_comments):
    for post_url, comment in post_comments.items():
        media_id = cl.media_pk_from_url(post_url)
        cl.media_comment(media_id, comment)

def post_content(cl, content, caption):
    cl.photo_upload(content, caption)

def change_profile(cl, name=None, bio=None):
    if name:
        cl.account_edit(name=name)
    if bio:
        cl.account_edit(biography=bio)

def run_schedule(logged_in_clients):
    # Schedule for posting reels 5 times a day
    reel_times = [
        "00:00:00",
        "03:00:00",
        "09:00:00",
        "12:00:00",
        "15:00:00",
        "18:00:00",
        "21:00:00"
    ]
    while True:
        now = datetime.now()
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        for item in reel_times:
            post_time = datetime.strptime(item, "%H:%M:%S").replace(
                year=now.year, month=now.month, day=now.day)
            print(f"Checking schedule: {item} | Post time: {post_time.strftime('%Y-%m-%d %H:%M:%S')}")
            # Check if the current time matches the post time
            if now >= post_time and now < post_time + timedelta(seconds=10):
                for cl in logged_in_clients:
                    try:
                        print("Attempting to post reels")
                        post_reels(cl)
                        print("Reels has successfully posted")
                        time.sleep(10)  # Wait for a short time before checking the next post
                    except Exception as e:
                        print("Failed to post reels:", e)
        time.sleep(5)  # Check the schedule every 5 seconds

def post_reels(cl):
    def select_random_image():
        image_folder = "C:\\Users\\Yiğit\\Desktop\\Instagram Bot\\images"
        images = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg'))]
        return random.choice(images)

    def get_hashtags():
        hashtags = "#fyp #fy #tech #techtok #programming #soft #software #code #it #technology"
        return hashtags

    def resize_image(image_path, target_width, target_height, scale=0.8):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            new_width = int(target_width * scale)
            new_height = int(new_width / img_ratio)
        else:
            new_height = int(target_height * scale)
            new_width = int(new_height * img_ratio)

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_path = f"resized_{os.path.basename(image_path)}"
        resized_img.save(resized_path)
        return resized_path

    def create_reels_video(image_path, video_path, output_path):
        video = mp.VideoFileClip(video_path)
        resized_image_path = resize_image(image_path, video.w, video.h)
        image_clip = mp.ImageClip(resized_image_path).set_duration(video.duration)

        
        # Calculate the position of the image to center it
        image_clip = image_clip.set_position("center")

        final_video = mp.CompositeVideoClip([video, image_clip])
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

    def post_to_instagram():
        image_path = select_random_image()
        caption = get_hashtags()
        
        video_path = "C:\\Users\\Yiğit\\Desktop\\Instagram Bot\\videos\\video.mp4"  # For example, an existing video
        output_path = "C:\\Users\\Yiğit\\Desktop\\Instagram Bot\\output\\final_reels.mp4"  # Where to save the created video

        
        # Adding images on video
        create_reels_video(image_path, video_path, output_path)
        
        
        # Video upload process
        cl.clip_upload(output_path, caption=caption)

        
        # Send the image file to the recycle bin / You can change this to delete the image but I sometimes reuse it ^^
        if os.path.exists(image_path):
            send2trash(image_path)
            print(f"{image_path} sent to recycle bin.")

    post_to_instagram()

# Tkinter GUI setup
class InstagramBotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Instagram Bot by Yiğidosantos")
        self.geometry("500x700")
        self.configure(bg="#f0f0f0")
        icon = tk.PhotoImage(file="C:\\Users\\Yiğit\\Desktop\\Instagram Bot\\icon.png")
        self.iconphoto(True, icon)
        self.logged_in_clients = []
        self.client_usernames = []

        # Frame for title
        title_frame = tk.Frame(self, bg="#3b5998")
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Instagram Bot", bg="#3b5998", fg="white", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        # Frame for buttons
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(pady=20)

        # Account selection
        selection_frame = tk.Frame(button_frame, bg="#f0f0f0")
        selection_frame.pack(pady=10)
        selection_label = tk.Label(selection_frame, text="Select Account(s):", bg="#f0f0f0", font=("Arial", 12, "bold"))
        selection_label.pack(side=tk.LEFT)
        
        listbox_frame = tk.Frame(selection_frame, bg="#f0f0f0")
        listbox_frame.pack(side=tk.LEFT, padx=10)
        
        self.account_listbox = tk.Listbox(listbox_frame, selectmode=MULTIPLE, width=30, height=6, bd=2, relief=tk.GROOVE, font=("Arial", 10))
        self.account_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.account_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.account_listbox.yview)

        # Login button
        self.login_button = self.create_button(button_frame, "Login", self.login_action)
        self.login_button.pack(pady=10)

        # Other buttons for actions
        self.follow_button = self.create_button(button_frame, "Follow Users", self.follow_users_action)
        self.like_button = self.create_button(button_frame, "Like Posts", self.like_posts_action)
        self.comment_button = self.create_button(button_frame, "Comment on Posts", self.comment_posts_action)
        self.reels_button = self.create_button(button_frame, "Post Reels", self.post_reels_action)
        self.post_button = self.create_button(button_frame, "Post Content", self.post_content_action)
        self.profile_button = self.create_button(button_frame, "Change Profile", self.change_profile_action)
        self.schedule_button = self.create_button(button_frame, "Run Schedule", self.run_schedule_action)

        self.disable_buttons()

    def create_button(self, frame, text, command):
        button = tk.Button(frame, text=text, command=command, bg="#3b5998", fg="white", font=("Arial", 12, "bold"), width=20, relief=tk.RAISED)
        button.pack(pady=10)
        button.bind("<Enter>", self.on_enter)
        button.bind("<Leave>", self.on_leave)
        return button

    def on_enter(self, e):
        e.widget['background'] = '#2b3e7e'

    def on_leave(self, e):
        e.widget['background'] = '#3b5998'

    def disable_buttons(self):
        self.follow_button.config(state=tk.DISABLED, text="Disabled")
        self.like_button.config(state=tk.DISABLED, text="Disabled")
        self.comment_button.config(state=tk.DISABLED, text="Disabled")
        self.post_button.config(state=tk.DISABLED, text="Disabled")
        self.reels_button.config(state=tk.DISABLED, text="Disabled")
        self.profile_button.config(state=tk.DISABLED, text="Disabled")
        self.schedule_button.config(state=tk.DISABLED, text="Disabled")

    def enable_buttons(self):
        self.login_button.config(text="Login", state=tk.NORMAL)
        self.follow_button.config(state=tk.NORMAL, text="Follow Users")
        self.like_button.config(state=tk.NORMAL, text="Like Posts")
        self.comment_button.config(state=tk.NORMAL, text="Comment on Posts")
        self.post_button.config(state=tk.NORMAL, text="Post Content")
        self.reels_button.config(state=tk.NORMAL, text="Post Reels")
        self.profile_button.config(state=tk.NORMAL, text="Change Profile")
        self.schedule_button.config(state=tk.NORMAL, text="Run Schedule")

    def update_account_listbox(self):
        self.account_listbox.delete(0, tk.END)
        for idx, username in enumerate(self.client_usernames, start=1):
            self.account_listbox.insert(tk.END, f"{idx}) {username}")

    def login_action(self):
        username = simpledialog.askstring("Log In", "Enter your Instagram username:", parent=self)
        password = simpledialog.askstring("Log In", "Enter your Instagram password:", show='*', parent=self)
        if username and password:
            try:
                cl = login(username, password)
                self.logged_in_clients.append(cl)
                self.client_usernames.append(username)
                self.update_account_listbox()
                self.enable_buttons()
                messagebox.showinfo("Info", "Logged in successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {str(e)}")

    def get_selected_clients(self):
        selected_indices = self.account_listbox.curselection()
        selected_clients = [self.logged_in_clients[i] for i in selected_indices]
        if selected_clients:
            return selected_clients
        else:
            messagebox.showerror("Error", "Please select at least one account.")
            return None

    def follow_users_action(self):
        clients = self.get_selected_clients()
        if clients:
            usernames = simpledialog.askstring("Follow Users", "Enter usernames to follow (comma-separated):", parent=self)
            if usernames:
                usernames_list = [username.strip() for username in usernames.split(",")]
                for cl in clients:
                    follow_users(cl, usernames_list)
                messagebox.showinfo("Info", "Followed users successfully")

    def like_posts_action(self):
        clients = self.get_selected_clients()
        if clients:
            post_urls = simpledialog.askstring("Like Posts", "Enter post URLs to like (comma-separated):", parent=self)
            if post_urls:
                post_urls_list = [post_url.strip() for post_url in post_urls.split(",")]
                for cl in clients:
                    like_posts(cl, post_urls_list)
                messagebox.showinfo("Info", "Liked posts successfully")

    def comment_posts_action(self):
        clients = self.get_selected_clients()
        if clients:
            post_urls = simpledialog.askstring("Comment on Posts", "Enter post URLs to comment on (comma-separated):", parent=self)
            comments = simpledialog.askstring("Comment on Posts", "Enter comments for posts (comma-separated):", parent=self)
            if post_urls and comments:
                post_urls_list = [post_url.strip() for post_url in post_urls.split(",")]
                comments_list = [comment.strip() for comment in comments.split(",")]
                post_comments = dict(zip(post_urls_list, comments_list))
                for cl in clients:
                    comment_on_posts(cl, post_comments)
                messagebox.showinfo("Info", "Commented on posts successfully")

    def post_content_action(self):
        clients = self.get_selected_clients()
        if clients:
            content = simpledialog.askstring("Post Content", "Enter path to content:", parent=self)
            caption = simpledialog.askstring("Post Content", "Enter caption for the content:", parent=self)
            if content and caption:
                for cl in clients:
                    post_content(cl, content, caption)
                messagebox.showinfo("Info", "Posted content successfully")

    def change_profile_action(self):
        clients = self.get_selected_clients()
        if clients:
            name = simpledialog.askstring("Change Profile", "Enter new name:", parent=self)
            bio = simpledialog.askstring("Change Profile", "Enter new bio:", parent=self)
            if name or bio:
                for cl in clients:
                    change_profile(cl, name=name, bio=bio)
                messagebox.showinfo("Info", "Changed profile successfully")

    def post_reels_action(self):
        clients = self.get_selected_clients()
        if clients:
            try:
                for cl in clients:
                    post_reels(cl)
                messagebox.showinfo("Info", "Posted reels successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to post reels: {str(e)}")

    def run_schedule_action(self):
        threading.Thread(target=run_schedule, args=(self.logged_in_clients,)).start()
        messagebox.showinfo("Info", "Schedule running")

if __name__ == "__main__":
    app = InstagramBotApp()
    app.mainloop()
