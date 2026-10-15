"""Streamlit frontend for Forgetting Curve."""

import os
from datetime import datetime

import requests
import streamlit as st


st.set_page_config(
    page_title="Forgetting Curve",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1"

# Secrets are configured on the hosting platform, not committed to Git.
try:
    API_BASE_URL = st.secrets.get("API_BASE_URL", "")
except Exception:
    API_BASE_URL = ""

API_BASE_URL = (
    API_BASE_URL
    or os.getenv("API_BASE_URL", DEFAULT_API_URL)
).rstrip("/")


st.markdown(
    """
    <style>
    .stApp {
        background: #f5f7f3;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e3e9e1;
    }

    h1, h2, h3 {
        color: #263d2f;
    }

    [data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border: 1px solid #e1e8df;
        border-radius: 14px;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: #245d49;
        border: 1px solid #245d49;
        color: white;
        border-radius: 9px;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 9px;
    }

    .hero {
        background: linear-gradient(115deg, #24543f, #347154);
        color: #ffffff;
        padding: 28px 30px;
        border-radius: 18px;
        margin-bottom: 22px;
    }

    .hero h2 {
        color: #ffffff;
        margin-bottom: 8px;
    }

    .hero p {
        color: #dcebe0;
        margin-bottom: 0;
    }

    .muted {
        color: #768278;
        font-size: 0.9rem;
    }

    .tag {
        color: #376b4e;
        background: #e8f2e7;
        padding: 3px 8px;
        margin-right: 5px;
        border-radius: 6px;
        font-size: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    payload: dict | None = None,
    params: dict | None = None,
):
    """Make an HTTP request to the Forgetting Curve API."""

    headers = {"Accept": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            headers=headers,
            json=payload,
            params=params,
            timeout=20,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            "Cannot reach the API. Check that FastAPI is running "
            "and API_BASE_URL is correct."
        ) from exc

    if not response.ok:
        try:
            body = response.json()
            detail = body.get("detail", "Request failed")

            if isinstance(detail, list):
                detail = "; ".join(
                    item.get("msg", "Invalid input")
                    for item in detail
                )
        except (ValueError, AttributeError):
            detail = f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise PermissionError(
                "Your session is invalid or expired. Please sign in again."
            )

        raise RuntimeError(str(detail))

    if response.status_code == 204:
        return None

    if not response.content:
        return None

    return response.json()


def clear_session():
    """Log out and clear in-memory authentication state."""

    st.session_state.pop("token", None)
    st.session_state.pop("user", None)
    st.session_state["auth_notice"] = "You have signed out."
    st.rerun()


def parse_tags(value: str) -> list[str]:
    """Convert comma-separated text into unique tags."""

    return list(
        dict.fromkeys(
            tag.strip()
            for tag in value.split(",")
            if tag.strip()
        )
    )


def format_date(value: str | None) -> str:
    """Format an ISO timestamp for display."""

    if not value:
        return "Date unavailable"

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).strftime("%b %d, %Y")
    except ValueError:
        return value


def show_auth_screen():
    """Display registration and login forms."""

    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown("### 🧠 Forgetting Curve")
        st.markdown("")
        st.markdown("")
        st.markdown("# Learn it today.")
        st.markdown("# Remember it tomorrow.")
        st.write(
            "Build lasting knowledge with active recall and "
            "spaced repetition."
        )

        st.info(
            "Capture what you learn. Test what you remember. "
            "Return to it at the right time."
        )

    with right:
        st.markdown("## Your learning space")
        login_tab, register_tab = st.tabs(
            ["Sign in", "Create account"]
        )

        with login_tab:
            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                try:
                    result = api_request(
                        "POST",
                        "/auth/login",
                        payload={
                            "email": email.strip(),
                            "password": password,
                        },
                    )

                    st.session_state["token"] = result["access_token"]
                    st.session_state["user"] = api_request(
                        "GET",
                        "/auth/me",
                        token=result["access_token"],
                    )
                    st.rerun()

                except Exception as exc:
                    st.error(str(exc))

        with register_tab:
            with st.form("register_form"):
                email = st.text_input(
                    "Email address",
                    key="register_email",
                )
                password = st.text_input(
                    "Password (12–128 characters)",
                    type="password",
                    key="register_password",
                )

                submitted = st.form_submit_button(
                    "Create account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                try:
                    api_request(
                        "POST",
                        "/auth/register",
                        payload={
                            "email": email.strip(),
                            "password": password,
                        },
                    )

                    st.success(
                        "Account created. Open Sign in to continue."
                    )

                except Exception as exc:
                    st.error(str(exc))

        notice = st.session_state.pop("auth_notice", None)
        if notice:
            st.success(notice)


def fetch_concepts(token: str, archived: bool = False) -> list[dict]:
    """Retrieve concepts belonging to the authenticated user."""

    return api_request(
        "GET",
        "/concepts",
        token=token,
        params={
            "archived": archived,
            "limit": 100,
            "offset": 0,
        },
    )


def concept_form(
    token: str,
    concept: dict | None = None,
    *,
    form_key: str,
):
    """Show a create or update form."""

    editing = concept is not None
    title = concept["title"] if editing else ""
    question = concept["question"] if editing else ""
    answer = concept["answer"] if editing else ""
    subject = concept.get("subject") or "" if editing else ""
    tags = ", ".join(concept.get("tags", [])) if editing else ""

    with st.form(form_key):
        new_title = st.text_input(
            "Title",
            value=title,
            max_chars=200,
        )
        new_subject = st.text_input(
            "Subject",
            value=subject,
            max_chars=120,
        )
        new_question = st.text_area(
            "Question",
            value=question,
            max_chars=5000,
        )
        new_answer = st.text_area(
            "Answer",
            value=answer,
            max_chars=10000,
        )
        new_tags = st.text_input(
            "Tags (comma-separated)",
            value=tags,
            help="Example: Python, functions, interview",
        )

        submitted = st.form_submit_button(
            "Save changes" if editing else "Create concept",
            type="primary",
        )

    if not submitted:
        return

    payload = {
        "title": new_title.strip(),
        "question": new_question.strip(),
        "answer": new_answer.strip(),
        "subject": new_subject.strip() or None,
        "tags": parse_tags(new_tags),
    }

    if not payload["title"] or not payload["question"] or not payload["answer"]:
        st.error("Title, question, and answer are required.")
        return

    try:
        if editing:
            api_request(
                "PATCH",
                f"/concepts/{concept['id']}",
                token=token,
                payload=payload,
            )
            st.success("Concept updated.")
        else:
            api_request(
                "POST",
                "/concepts",
                token=token,
                payload=payload,
            )
            st.success("Concept created.")

        st.rerun()

    except Exception as exc:
        st.error(str(exc))


def main():
    """Render the authenticated application."""

    token = st.session_state.get("token")

    if not token:
        show_auth_screen()
        st.stop()

    if not st.session_state.get("user"):
        try:
            st.session_state["user"] = api_request(
                "GET",
                "/auth/me",
                token=token,
            )
        except Exception:
            st.session_state.pop("token", None)
            st.session_state.pop("user", None)
            st.session_state["auth_notice"] = (
                "Your session expired. Please sign in again."
            )
            st.rerun()

    user = st.session_state["user"]

    with st.sidebar:
        st.markdown("## 🧠 Forgetting Curve")
        st.caption("Your personal learning space")
        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Overview",
                "Concept library",
                "Review session",
                "Insights",
                "Settings",
            ],
        )

        st.divider()
        st.caption(user["email"])

        if st.button("Sign out", use_container_width=True):
            clear_session()

    try:
        active_concepts = fetch_concepts(token, archived=False)
        archived_concepts = fetch_concepts(token, archived=True)
    except PermissionError:
        st.session_state.pop("token", None)
        st.session_state.pop("user", None)
        st.rerun()
    except Exception as exc:
        st.error(f"Could not load your concepts: {exc}")
        st.stop()

    if page == "Overview":
        st.title("Your learning space")
        st.write(
            "Capture what matters. Challenge what you remember."
        )

        st.markdown(
            """
            <div class="hero">
                <h2>Make learning stick.</h2>
                <p>
                    Build knowledge one concept at a time.
                    Your dashboard uses your real saved concepts.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        subjects = {
            item.get("subject")
            for item in active_concepts
            if item.get("subject")
        }

        tagged = sum(
            bool(item.get("tags"))
            for item in active_concepts
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Active concepts", len(active_concepts))
        col2.metric("Archived", len(archived_concepts))
        col3.metric("Subjects", len(subjects))
        col4.metric("Tagged concepts", tagged)

        st.subheader("Recently added")

        if not active_concepts:
            st.info(
                "Your learning library is empty. "
                "Open Concept library to create your first concept."
            )
        else:
            for concept in active_concepts[:5]:
                with st.container(border=True):
                    st.markdown(f"**{concept['title']}**")
                    st.caption(
                        f"{concept.get('subject') or 'General'} · "
                        f"Added {format_date(concept.get('created_at'))}"
                    )
                    st.write(concept["question"])

        st.caption(
            "Review totals and recall statistics will appear "
            "after the review-history API is implemented."
        )

    elif page == "Concept library":
        st.title("Concept library")
        st.write("Create, organize, and maintain your learning concepts.")

        with st.expander("➕ Add a new concept", expanded=False):
            concept_form(
                token,
                form_key="new_concept_form",
            )

        active_tab, archived_tab = st.tabs(
            [
                f"Active ({len(active_concepts)})",
                f"Archived ({len(archived_concepts)})",
            ]
        )

        search = st.text_input(
            "Search concepts",
            placeholder="Search titles, questions, answers, subjects, or tags...",
        ).strip().lower()

        def matches(concept: dict) -> bool:
            searchable = " ".join(
                [
                    concept["title"],
                    concept["question"],
                    concept["answer"],
                    concept.get("subject") or "",
                    *concept.get("tags", []),
                ]
            ).lower()

            return search in searchable

        with active_tab:
            matching = [
                concept
                for concept in active_concepts
                if matches(concept)
            ]

            if not matching:
                st.info(
                    "No matching active concepts. "
                    "Create a concept or try another search."
                )

            for concept in matching:
                with st.expander(concept["title"]):
                    st.caption(
                        f"Subject: {concept.get('subject') or 'General'}"
                    )
                    st.markdown("**Question**")
                    st.write(concept["question"])
                    st.markdown("**Answer**")
                    st.write(concept["answer"])
                    st.caption(
                        "Tags: "
                        + (
                            ", ".join(concept.get("tags", []))
                            or "None"
                        )
                    )

                    with st.expander("Edit this concept"):
                        concept_form(
                            token,
                            concept,
                            form_key=f"edit_{concept['id']}",
                        )

                    col1, col2 = st.columns(2)

                    if col1.button(
                        "Archive",
                        key=f"archive_{concept['id']}",
                    ):
                        try:
                            api_request(
                                "PATCH",
                                f"/concepts/{concept['id']}",
                                token=token,
                                payload={"is_archived": True},
                            )
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

                    if col2.button(
                        "Delete",
                        key=f"delete_{concept['id']}",
                    ):
                        st.session_state["delete_concept_id"] = concept["id"]

                    if st.session_state.get("delete_concept_id") == concept["id"]:
                        st.warning(
                            "This permanently deletes the concept. "
                            "Confirm to continue."
                        )

                        if st.button(
                            "Confirm permanent deletion",
                            key=f"confirm_delete_{concept['id']}",
                            type="primary",
                        ):
                            try:
                                api_request(
                                    "DELETE",
                                    f"/concepts/{concept['id']}",
                                    token=token,
                                )
                                st.session_state.pop("delete_concept_id", None)
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))

        with archived_tab:
            matching = [
                concept
                for concept in archived_concepts
                if matches(concept)
            ]

            if not matching:
                st.info("No matching archived concepts.")

            for concept in matching:
                with st.container(border=True):
                    st.markdown(f"**{concept['title']}**")
                    st.write(concept["question"])

                    if st.button(
                        "Restore concept",
                        key=f"restore_{concept['id']}",
                    ):
                        try:
                            api_request(
                                "PATCH",
                                f"/concepts/{concept['id']}",
                                token=token,
                                payload={"is_archived": False},
                            )
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

    elif page == "Review session":
        st.title("Review session")
        st.info(
            "The scheduler is implemented, but the API for persisted "
            "review states, due cards, ratings, and review history "
            "still needs to be connected."
        )
        st.write(
            "The next milestone will let you answer a due card, reveal "
            "its answer, rate your recall, and save the next review time."
        )

    elif page == "Insights":
        st.title("Learning insights")
        st.info(
            "Real review analytics will appear when review logs "
            "and statistics endpoints are available."
        )

        st.metric("Concepts in your active library", len(active_concepts))
        st.caption(
            "No review success rate or retention metric is fabricated."
        )

    elif page == "Settings":
        st.title("Account settings")

        with st.container(border=True):
            st.subheader("Your account")
            st.write(f"**Email:** {user['email']}")
            st.write(
                "**Member since:** "
                + format_date(user.get("created_at"))
            )

        st.warning(
            "This development frontend keeps the bearer token in "
            "Streamlit session state. Before a production launch, "
            "we should review the authentication and session strategy."
        )


if __name__ == "__main__":
    main()