(() => {
  "use strict";

  // All channel tags intentionally fall back to the existing PartnerNet tracking ID
  // until the channel-specific IDs are created in Amazon PartnerNet.
  const DEFAULT_TAG = "workflowgui02-21";
  const TAGS = {
    pinterest: "workflowpinterest-21",
    youtube: "workflowyoutube-21",
    instagram: "workflowinstagram-21",
    tiktok: "workflowtiktok-21",
    seo: "workflowseo-21",
    direct: "workflowdirect-21",
  };

  const params = new URLSearchParams(window.location.search);
  const source = (params.get("utm_source") || "").trim().toLowerCase();

  function channelFromSource(value) {
    if (!value) return "";
    if (value.includes("pinterest")) return "pinterest";
    if (value === "youtube" || value === "yt" || value.includes("youtube")) return "youtube";
    if (value === "instagram" || value === "ig" || value.includes("instagram")) return "instagram";
    if (value === "tiktok" || value.includes("tiktok")) return "tiktok";
    if (["google", "bing", "duckduckgo", "ecosia", "search", "seo"].some((v) => value.includes(v))) return "seo";
    return "";
  }

  function channelFromReferrer() {
    if (!document.referrer) return "direct";
    try {
      const host = new URL(document.referrer).hostname.toLowerCase();
      if (host.includes("pinterest.")) return "pinterest";
      if (host.includes("youtube.") || host.includes("youtu.be")) return "youtube";
      if (host.includes("instagram.")) return "instagram";
      if (host.includes("tiktok.")) return "tiktok";
      if (["google.", "bing.", "duckduckgo.", "ecosia."].some((v) => host.includes(v))) return "seo";
    } catch (_) {
      // Ignore malformed referrers and keep the privacy-friendly direct fallback.
    }
    return "direct";
  }

  const channel = channelFromSource(source) || channelFromReferrer();
  const tag = TAGS[channel] || DEFAULT_TAG;

  document.querySelectorAll('a[href*="amazon.de"]').forEach((anchor) => {
    try {
      const url = new URL(anchor.href);
      if (!/(^|\.)amazon\.de$/i.test(url.hostname)) return;
      if (!url.searchParams.has("tag")) return;
      url.searchParams.set("tag", tag);
      anchor.href = url.toString();
      anchor.dataset.attributionChannel = channel;
    } catch (_) {
      // Keep the original affiliate link if a URL cannot be parsed.
    }
  });

  // Debug aid only. No cookies, localStorage, fingerprinting or external analytics calls.
  window.WGAffiliateAttribution = Object.freeze({ channel, tag });
})();
