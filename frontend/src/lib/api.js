import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api",
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const persistedState = window.localStorage.getItem("northstar-auth-store");

  if (!persistedState) {
    return config;
  }

  const { state } = JSON.parse(persistedState);

  if (state?.token) {
    config.headers.Authorization = `Bearer ${state.token}`;
  }

  return config;
});

export default api;
