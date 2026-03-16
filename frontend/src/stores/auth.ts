import { defineStore } from "pinia";
import { api } from "./api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as null | { id: number; email: string },
    error: "",
  }),
  actions: {
    async login(email: string, password: string) {
      this.error = "";
      try {
        const res = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
        localStorage.setItem("token", res.access_token);
        await this.fetchMe();
      } catch (e: any) {
        this.error = e.message;
      }
    },
    async register(email: string, password: string, disclaimerAccepted: boolean) {
      this.error = "";
      try {
        await api("/auth/register", {
          method: "POST",
          body: JSON.stringify({ email, password, disclaimer_accepted: disclaimerAccepted }),
        });
        await this.login(email, password);
      } catch (e: any) {
        this.error = e.message;
      }
    },
    async fetchMe() {
      try {
        this.user = await api("/auth/me");
      } catch {
        this.user = null;
      }
    },
    logout() {
      localStorage.removeItem("token");
      this.user = null;
    },
  },
});
