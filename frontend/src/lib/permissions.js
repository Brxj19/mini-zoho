export function hasAnyRole(user, roles = []) {
  if (!roles?.length) {
    return true;
  }

  return roles.includes(user?.role);
}
