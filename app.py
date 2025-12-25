import streamlit as st
from datetime import datetime
import os

FILES = [
    "users.txt",
    "posts.txt",
    "admin_requests.txt",
    "artist_requests.txt",
    "archive/data.txt"
]

for file in FILES:
    os.makedirs(os.path.dirname(file), exist_ok=True) if "/" in file else None
    if not os.path.exists(file):
        open(file, "w", encoding="utf-8").close()
import hashlib

# =========================
# 파일 경로
# =========================
USER_FILE = "users.txt"
ARTIST_REQ_FILE = "artist_requests.txt"
ADMIN_REQ_FILE = "admin_requests.txt"
ARCHIVE_DATA = "archive/data.txt"
ARCHIVE_IMG_DIR = "archive/images"
POSTS_FILE = "posts.txt"
os.makedirs(ARCHIVE_IMG_DIR, exist_ok=True)

# =========================
# 관리자 기본 계정 자동 생성
# =========================
admin_email = "admin@ryeojin.com"
admin_name = "려진족_사자"
admin_pw = "admin123"
hashed_pw = hashlib.sha256(admin_pw.encode()).hexdigest()

if not os.path.exists(USER_FILE):
    open(USER_FILE, "w").close()

admin_exists = False
with open(USER_FILE, "r") as f:
    for line in f.readlines():
        parts = line.strip().split("|")
        if len(parts) == 4 and parts[1] == admin_email:
            admin_exists = True
            break

if not admin_exists:
    with open(USER_FILE, "a") as f:
        f.write(f"{admin_name}|{admin_email}|{hashed_pw}|관리자\n")

# =========================
# 세션 초기화
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_type = None

# =========================
# CSS
# =========================
st.markdown("""
<style>
.main { background-color: #f7f7f9; }
h1,h2,h3 { color:#2e2e2e; }
.stButton>button { background-color:#b9a7d3; color:white; border-radius:12px; border:none; padding:0.4em 1em; }
input, textarea { border-radius:10px; padding:0.4em; }
hr { border:none; height:1px; background-color:#ddd; }
</style>
""", unsafe_allow_html=True)

# =========================
# 해시
# =========================
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# 회원가입 / 로그인
# =========================
if not st.session_state.logged_in:
    menu = st.radio("선택", ["로그인", "회원가입"])
    
    if menu == "회원가입":
        st.subheader("회원가입")
        username = st.text_input("닉네임")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        user_type = st.radio("사용자 유형", ["팬", "아티스트", "관리자"])

        if st.button("회원가입 완료"):
            if not username or not email or not password:
                st.warning("모두 입력하세요")
            else:
                if user_type == "팬":
                    with open(USER_FILE, "a") as f:
                        f.write(f"{username}|{email}|{hash_pw(password)}|팬\n")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_type = "팬"
                    st.success("회원가입 완료! 자동 로그인됩니다.")
                    st.experimental_rerun()
                elif user_type == "아티스트":
                    if not os.path.exists(ARTIST_REQ_FILE):
                        open(ARTIST_REQ_FILE, "w").close()
                    with open(ARTIST_REQ_FILE, "a") as f:
                        f.write(f"{username}|{email}|{hash_pw(password)}\n")
                    st.success("아티스트 가입 요청이 관리자에게 전달되었습니다.")
                else:  # 관리자 신청
                    if not os.path.exists(ADMIN_REQ_FILE):
                        open(ADMIN_REQ_FILE, "w").close()
                    with open(ADMIN_REQ_FILE, "a") as f:
                        f.write(f"{username}|{email}|{hash_pw(password)}\n")
                    st.success("관리자 가입 요청이 관리자에게 전달되었습니다.")

    else:
        st.subheader("로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            login_success = False
            if os.path.exists(USER_FILE):
                with open(USER_FILE, "r") as f:
                    for line in f.readlines():
                        u_name, u_email, u_pw, u_type = line.strip().split("|")
                        if u_email == email and u_pw == hash_pw(password):
                            st.session_state.logged_in = True
                            st.session_state.username = u_name
                            st.session_state.user_type = u_type
                            login_success = True
                            st.experimental_rerun()
            if not login_success:
                st.error("로그인 실패")

# =========================
# 로그인 후 화면
# =========================
else:
    st.sidebar.title(f"👋 {st.session_state.username}")
    menu = st.sidebar.radio("MENU", ["Home", "Archive", "Community", "Artist Upload", "Admin Panel"])

    # -------------------------
    # HOME - 인기 업로드
    # -------------------------
    if menu == "Home":
        st.title("💿 RYEOJIN Archive")
        st.caption("ryeojin의 기록을 모은 공간")

        st.subheader("🏆 인기 업로드")
        if os.path.exists(ARCHIVE_DATA):
            with open(ARCHIVE_DATA, "r", encoding="utf-8") as f:
                lines = f.readlines()
            posts_data = []
            for line in lines:
                parts = line.strip().split("|")
                if len(parts) < 5:
                    # likes가 없으면 0 추가
                    if len(parts) == 4:
                        parts.append("0")
                    else:
                        continue
                filename, caption_text, date_text, comments_text, likes_text = parts
                posts_data.append({
                    "filename": filename,
                    "caption": caption_text,
                    "date": date_text,
                    "comments": comments_text.split("||") if comments_text else [],
                    "likes": int(likes_text)
                })

            # likes 기준 내림차순 정렬
            posts_data.sort(key=lambda x: x["likes"], reverse=True)

            # 상위 5개 표시
            for i, p in enumerate(posts_data[:5]):
                path = f"{ARCHIVE_IMG_DIR}/{p['filename']}"
                if os.path.exists(path):
                    if p['filename'].endswith(".mp4"):
                        st.video(path)
                    else:
                        st.image(path, use_container_width=True)
                st.caption(f"{p['caption']} · {p['date']} · 👍 {p['likes']}")
                if st.button(f"좋아요 {i}"):
                    p['likes'] += 1
                    lines_idx = lines.index(line)
                    lines[lines_idx] = f"{p['filename']}|{p['caption']}|{p['date']}|{'||'.join(p['comments'])}|{p['likes']}\n"
                    with open(ARCHIVE_DATA, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    st.experimental_rerun()
        else:
            st.write("아직 업로드가 없습니다.")

    # -------------------------
    # COMMUNITY
    # -------------------------
    elif menu == "Community":
        st.title("💬 커뮤니티")
        st.caption("팬과 아티스트 모두 글 작성 가능")
        if not os.path.exists(POSTS_FILE):
            open(POSTS_FILE, "w", encoding="utf-8").close()
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            posts = f.readlines()

        message = st.text_input("메시지")
        if st.button("등록"):
            if not message:
                st.warning("메시지를 입력하세요.")
            else:
                date = datetime.now().strftime("%Y-%m-%d")
                with open(POSTS_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{st.session_state.username}|{message}|{date}\n")
                st.success("등록 완료!")
                st.experimental_rerun()

        st.divider()
        if posts:
            for post in reversed(posts):
                parts = post.strip().split("|")
                if len(parts) != 3:
                    continue
                name, msg, date = parts
                st.markdown(f"""
                <div style="
                    background:#fff;
                    padding:12px;
                    border-radius:12px;
                    margin-bottom:10px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);
                ">
                    <strong>{name}</strong>
                    <span style="color:#888;font-size:12px;"> {date}</span>
                    <p style="margin-top:6px;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("아직 메시지가 없습니다.")

    # -------------------------
    # ARTIST UPLOAD
    # -------------------------
    elif menu == "Artist Upload":
        st.title("🎨 Artist Upload")
        uploaded_file = st.file_uploader("사진/동영상 업로드", type=["jpg","png","jpeg","mp4"])
        caption = st.text_input("설명")
        if uploaded_file and st.button("업로드"):
            file_path = f"{ARCHIVE_IMG_DIR}/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            date = datetime.now().strftime("%Y-%m-%d")
            # 초기 likes=0
            with open(ARCHIVE_DATA, "a", encoding="utf-8") as f:
                f.write(f"{uploaded_file.name}|{caption}|{date}| |0\n")
            st.success("업로드 완료!")
            st.experimental_rerun()

        st.divider()
        if os.path.exists(ARCHIVE_DATA):
            with open(ARCHIVE_DATA, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i, line in enumerate(reversed(lines)):
                parts = line.strip().split("|")
                if len(parts) < 5:
                    continue
                filename, caption_text, date_text, comments_text, likes_text = parts
                comments = comments_text.split("||") if comments_text.strip() else []

                path = f"{ARCHIVE_IMG_DIR}/{filename}"
                if os.path.exists(path):
                    if filename.endswith(".mp4"):
                        st.video(path)
                    else:
                        st.image(path, use_container_width=True)
                st.caption(f"{caption_text} · {date_text} · 👍 {likes_text}")

                st.markdown("**댓글:**")
                for c in comments:
                    st.write(c)

                new_comment = st.text_input(f"댓글 작성 ({filename})", key=f"comment_{i}")
                if st.button("댓글 등록", key=f"btn_{i}"):
                    if new_comment:
                        comments.append(f"{st.session_state.username}: {new_comment}")
                        all_lines = [l for l in lines]
                        idx = len(lines) - 1 - i
                        all_lines[idx] = f"{filename}|{caption_text}|{date_text}|{'||'.join(comments)}|{likes_text}\n"
                        with open(ARCHIVE_DATA, "w", encoding="utf-8") as f:
                            f.writelines(all_lines)
                        st.experimental_rerun()

    # -------------------------
    # ADMIN PANEL
    # -------------------------
    elif menu == "Admin Panel":
        if st.session_state.user_type != "관리자":
            st.warning("관리자만 접근 가능합니다.")
        else:
            st.title("🛠 관리자 패널")

            # 신규 아티스트 요청
            st.subheader("신규 아티스트 요청")
            if not os.path.exists(ARTIST_REQ_FILE):
                open(ARTIST_REQ_FILE, "w").close()
            with open(ARTIST_REQ_FILE, "r") as f:
                requests = f.readlines()
            if requests:
                for i, line in enumerate(requests):
                    parts = line.strip().split("|")
                    if len(parts) < 3:
                        continue
                    uname, email, pw = parts
                    st.write(f"{uname} ({email})")
                    col1, col2 = st.columns(2)
                    if col1.button("승인", key=f"approve_{i}"):
                        with open(USER_FILE, "a") as uf:
                            uf.write(f"{uname}|{email}|{pw}|아티스트\n")
                        requests.pop(i)
                        with open(ARTIST_REQ_FILE, "w") as rf:
                            rf.writelines(requests)
                        st.success(f"{uname} 승인 완료")
                        st.experimental_rerun()
                    if col2.button("거부", key=f"reject_{i}"):
                        requests.pop(i)
                        with open(ARTIST_REQ_FILE, "w") as rf:
                            rf.writelines(requests)
                        st.info(f"{uname} 가입 요청 거부")
                        st.experimental_rerun()
            else:
                st.write("승인 대기 중인 아티스트가 없습니다.")

            st.divider()

            # 관리자 요청 처리
            st.subheader("신규 관리자 요청")
            if not os.path.exists(ADMIN_REQ_FILE):
                open(ADMIN_REQ_FILE, "w").close()
            with open(ADMIN_REQ_FILE, "r") as f:
                admin_reqs = f.readlines()
            if admin_reqs:
                for i, line in enumerate(admin_reqs):
                    parts = line.strip().split("|")
                    if len(parts) < 3:
                        continue
                    uname, email, pw = parts
                    st.write(f"{uname} ({email})")
                    col1, col2 = st.columns(2)
                    if col1.button("승인", key=f"admin_approve_{i}"):
                        with open(USER_FILE, "a") as uf:
                            uf.write(f"{uname}|{email}|{pw}|관리자\n")
                        admin_reqs.pop(i)
                        with open(ADMIN_REQ_FILE, "w") as af:
                            af.writelines(admin_reqs)
                        st.success(f"{uname} 관리자 승인 완료")
                        st.experimental_rerun()
                    if col2.button("거부", key=f"admin_reject_{i}"):
                        admin_reqs.pop(i)
                        with open(ADMIN_REQ_FILE, "w") as af:
                            af.writelines(admin_reqs)
                        st.info(f"{uname} 관리자 가입 거부")
                        st.experimental_rerun()

    # -------------------------
    # LOGOUT
    # -------------------------
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_type = None

        st.experimental_rerun()
