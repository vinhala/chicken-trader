import { createRouter, createWebHistory } from "vue-router";
import LandingView from "../views/LandingView.vue";
import OpportunitiesView from "../views/OpportunitiesView.vue";
import OpportunityDetailView from "../views/OpportunityDetailView.vue";
import FollowedIdeasView from "../views/FollowedIdeasView.vue";
import NotificationsView from "../views/NotificationsView.vue";
import WatchlistView from "../views/WatchlistView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: LandingView },
    { path: "/market", component: OpportunitiesView },
    { path: "/opportunities/:id", component: OpportunityDetailView },
    { path: "/followed", component: FollowedIdeasView },
    { path: "/notifications", component: NotificationsView },
    { path: "/watchlist", component: WatchlistView },
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/:pathMatch(.*)*", redirect: "/market" },
  ],
});

router.beforeEach((to) => {
  const publicPaths = new Set(["/", "/login", "/register"]);
  const token = localStorage.getItem("token");

  if (!publicPaths.has(to.path) && !token) {
    return { path: "/" };
  }
  if (publicPaths.has(to.path) && token) {
    return { path: "/market" };
  }
  return true;
});

router.afterEach((to) => {
  const umami = window.umami;
  if (!umami) {
    return;
  }

  const location = to.fullPath || to.path;
  if (typeof umami.trackView === "function") {
    umami.trackView(location);
    return;
  }

  if (typeof umami.track === "function") {
    umami.track(() => ({ url: location }));
  }
});

export default router;
