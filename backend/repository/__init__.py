# ==============================================
# MoodFlow - Repository Package
# ==============================================
# This package handles all data storage operations
# Split by domain for better organization
# ==============================================

from repository.user_repo import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    check_user_password,
    user_to_dict,
    update_user,
)

from repository.task_repo import (
    create_task,
    get_tasks_by_user,
    get_incomplete_tasks_by_user,
    get_task_by_id,
    get_existing_task,
    update_task,
    delete_task,
    count_tasks,
    get_today_due_tasks,
)

from repository.emotion_repo import (
    create_emotion_entry,
    get_emotion_entry_by_date,
    get_emotion_history_since,
    get_all_emotions,
    get_emotion_by_id,
    get_emotion_by_name,
)

from repository.favorites_repo import (
    get_user_book_favorites,
    add_book_favorite,
    remove_book_favorite,
    get_user_music_favorites,
    add_music_favorite,
    remove_music_favorite,
)

from repository.book_repo import (
    get_all_book_tags,
    get_tag_by_slug,
    get_all_books,
    get_books_by_tags,
    get_all_tags_as_dict,
    get_tag_objects_for_book,
)

from repository.music_repo import (
    get_all_music,
    get_music_by_emotion,
)

from repository.admin_repo import (
    get_all_users_stats,
    get_overall_emotion_stats,
    get_overall_task_stats,
)
