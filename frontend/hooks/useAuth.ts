"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import type {
  APIResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
} from "@/lib/types";

export function useAuth() {
  const router = useRouter();
  const { user, isAuthenticated, setAuth, logout: clearAuth } = useAuthStore();

  const login = useCallback(
    async (data: LoginRequest) => {
      const res = await api.post<APIResponse<LoginResponse>>(
        "/auth/login",
        data
      );
      const { access_token, user: u } = res.data.data!;
      setAuth(u, access_token);
      if (u.role === "lawyer") router.push("/lawyer");
      else if (u.role === "admin") router.push("/admin");
      else router.push("/");
    },
    [setAuth, router]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      const res = await api.post<APIResponse<RegisterResponse>>(
        "/auth/register",
        data
      );
      return res.data.data!;
    },
    []
  );

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // ignore
    }
    clearAuth();
    router.push("/login");
  }, [clearAuth, router]);

  return { user, isAuthenticated, login, register, logout };
}
