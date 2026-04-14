export {};

declare global {
  interface RuntimeEnv {
    API_BASE_URL?: string;
    UMAMI_SCRIPT_URL?: string;
    UMAMI_WEBSITE_ID?: string;
    UMAMI_HOST_URL?: string;
  }

  interface UmamiClient {
    track?: ((payload?: unknown) => void) | ((transform: (payload: { url?: string }) => { url?: string }) => void);
    trackView?: (url?: string) => void;
  }

  interface Window {
    __APP_ENV__?: RuntimeEnv;
    umami?: UmamiClient;
  }
}
