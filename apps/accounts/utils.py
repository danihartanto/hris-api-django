def user_has_permission(user, perm_code: str):
    if user.is_superuser:
        return True

    role = getattr(user, "role", None)
    if not role:
        return False

    return role.permissions.filter(code=perm_code).exists()
