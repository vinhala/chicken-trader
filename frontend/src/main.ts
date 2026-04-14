import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./styles.css";

function initUmami(): void {
  const runtimeEnv = window.__APP_ENV__;
  if (!runtimeEnv) {
    return;
  }

  const scriptUrl = runtimeEnv.UMAMI_SCRIPT_URL?.trim();
  const websiteId = runtimeEnv.UMAMI_WEBSITE_ID?.trim();

  if (!scriptUrl || !websiteId) {
    return;
  }

  if (document.querySelector('script[data-analytics-provider="umami"]')) {
    return;
  }

  const script = document.createElement("script");
  script.defer = true;
  script.src = scriptUrl;
  script.setAttribute("data-website-id", websiteId);
  script.setAttribute("data-analytics-provider", "umami");

  const hostUrl = runtimeEnv.UMAMI_HOST_URL?.trim();
  if (hostUrl) {
    script.setAttribute("data-host-url", hostUrl);
  }

  document.head.appendChild(script);
}

initUmami();

createApp(App).use(createPinia()).use(router).mount("#app");
