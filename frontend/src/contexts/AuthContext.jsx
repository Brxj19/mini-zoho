import { createContext, useContext, useEffect, useState } from "react";

import api, { setAuthHeader } from "../lib/api";

const AuthContext = createContext(null);
const ACCESS_TOKEN_STORAGE_KEY = "northstar.inventory.accessToken";
const REFRESH_TOKEN_STORAGE_KEY = "northstar.inventory.refreshToken";

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    const storedAccessToken = window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
    const storedRefreshToken = window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);

    if (!storedAccessToken) {
      setIsLoading(false);
      return;
    }

    synchronizeSession(storedAccessToken, storedRefreshToken);
  }, []);

  useEffect(() => {
    setAuthHeader(accessToken);
  }, [accessToken]);

  async function synchronizeSession(nextAccessToken, nextRefreshToken) {
    try {
      const profile = await loadProfile(nextAccessToken);
      persistSession({
        access_token: nextAccessToken,
        refresh_token: nextRefreshToken,
        user: profile,
        tenant: profile.tenant,
      });
    } catch (error) {
      if (!nextRefreshToken) {
        clearSession();
        setIsLoading(false);
        return;
      }

      try {
        const response = await api.post("/auth/refresh", { refresh_token: nextRefreshToken });
        persistSession(response.data);
      } catch {
        clearSession();
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function loadProfile(tokenToUse) {
    const response = await api.get("/auth/me", {
      headers: {
        Authorization: `Bearer ${tokenToUse}`,
      },
    });
    return response.data;
  }

  function persistSession(session) {
    window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, session.access_token);
    window.localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, session.refresh_token);
    setAccessToken(session.access_token);
    setRefreshToken(session.refresh_token);
    setUser(session.user);
    setTenant(session.tenant ?? session.user?.tenant ?? null);
    setAuthError(null);
  }

  function clearSession() {
    window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    setTenant(null);
  }

  async function login(credentials) {
    const response = await api.post("/auth/login", credentials);
    persistSession(response.data);
    return response.data;
  }

  async function register(payload) {
    const response = await api.post("/auth/register", payload);
    persistSession(response.data);
    return response.data;
  }

  async function refreshProfile() {
    if (!accessToken) {
      return null;
    }

    const profile = await loadProfile(accessToken);
    setUser(profile);
    setTenant(profile.tenant ?? profile.user?.tenant ?? null);
    return profile;
  }

  async function logout() {
    try {
      if (accessToken) {
        await api.post("/auth/logout");
      }
    } catch {
      // Logout is stateless; local cleanup is the source of truth for the UI.
    } finally {
      clearSession();
    }
  }

  function clearAuthError() {
    setAuthError(null);
  }

  function setErrorFromResponse(error, fallbackMessage) {
    const detail = error?.response?.data?.detail ?? fallbackMessage;
    setAuthError(detail);
    return detail;
  }

  const value = {
    isAuthenticated: Boolean(accessToken && user),
    accessToken,
    refreshToken,
    user,
    tenant,
    isLoading,
    authError,
    clearAuthError,
    async login(credentials) {
      try {
        return await login(credentials);
      } catch (error) {
        throw new Error(setErrorFromResponse(error, "Unable to sign in."));
      }
    },
    async register(payload) {
      try {
        return await register(payload);
      } catch (error) {
        throw new Error(setErrorFromResponse(error, "Unable to create your workspace."));
      }
    },
    async logout() {
      await logout();
    },
    async refreshProfile() {
      try {
        return await refreshProfile();
      } catch (error) {
        throw new Error(setErrorFromResponse(error, "Unable to refresh your workspace profile."));
      }
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
