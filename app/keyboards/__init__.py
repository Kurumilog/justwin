# Keyboards package

from .main_menu import (
    get_main_menu_keyboard,
    get_admin_cabinet_keyboard,
    get_back_button,
    get_back_to_cabinet_button
)

from .task_keyboards import (
    get_task_management_keyboard,
    get_task_list_keyboard,
    get_task_actions_keyboard,
    get_task_confirm_delete_keyboard
)

from .form_keyboards import (
    get_form_management_keyboard,
    get_form_list_keyboard,
    get_form_actions_keyboard,
    get_form_confirm_delete_keyboard,
    get_form_task_selection_keyboard,
    get_form_edit_options_keyboard
)

from .check_keyboards import (
    get_check_menu_keyboard,
    get_form_selection_keyboard,
    get_check_grade_keyboard,
    get_error_report_keyboard,
    get_check_complete_keyboard,
    get_check_list_keyboard,
    get_check_cancel_confirm_keyboard
)

__all__ = [
    # Main menu
    'get_main_menu_keyboard',
    'get_admin_cabinet_keyboard',
    'get_back_button',
    'get_back_to_cabinet_button',
    
    # Tasks
    'get_task_management_keyboard',
    'get_task_list_keyboard',
    'get_task_actions_keyboard',
    'get_task_confirm_delete_keyboard',
    
    # Forms
    'get_form_management_keyboard',
    'get_form_list_keyboard',
    'get_form_actions_keyboard',
    'get_form_confirm_delete_keyboard',
    'get_form_task_selection_keyboard',
    'get_form_edit_options_keyboard',
    
    # Checks
    'get_check_menu_keyboard',
    'get_form_selection_keyboard',
    'get_check_grade_keyboard',
    'get_error_report_keyboard',
    'get_check_complete_keyboard',
    'get_check_list_keyboard',
    'get_check_cancel_confirm_keyboard',
]
