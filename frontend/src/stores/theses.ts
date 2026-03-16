import { defineStore } from "pinia";
import { api } from "./api";

export const useThesisStore = defineStore("theses", {
  state: () => ({
    items: [] as any[],
    error: "",
  }),
  actions: {
    async load() {
      this.error = "";
      try { this.items = await api("/theses"); }
      catch (e: any) { this.error = e.message; }
    },
  },
});
