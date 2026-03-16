import { createRouter, createWebHistory } from "vue-router";
import OpportunitiesView from "../views/OpportunitiesView.vue";
import OpportunityDetailView from "../views/OpportunityDetailView.vue";
import FollowedIdeasView from "../views/FollowedIdeasView.vue";
import NotificationsView from "../views/NotificationsView.vue";
import WatchlistView from "../views/WatchlistView.vue";
import BrokerSettingsView from "../views/BrokerSettingsView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: OpportunitiesView },
    { path: "/opportunities/:id", component: OpportunityDetailView },
    { path: "/followed", component: FollowedIdeasView },
    { path: "/notifications", component: NotificationsView },
    { path: "/watchlist", component: WatchlistView },
    { path: "/broker", component: BrokerSettingsView },
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});

router.beforeEach((to) => {
  const publicPaths = new Set(["/login", "/register"]);
  const token = localStorage.getItem("token");

  if (!publicPaths.has(to.path) && !token) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
  if (publicPaths.has(to.path) && token) {
    return { path: "/" };
  }
  return true;
});

export default router;
