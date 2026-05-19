# Lottie Animation Usage

This project uses hosted `.lottie` files through `@lottiefiles/dotlottie-react`.

## Animation key mapping

| Key | URL | Primary usage |
| --- | --- | --- |
| `appLoading` | `https://lottie.host/c4cc4163-1994-4321-b52f-356077798735/CYt2M3yTRw.lottie` | Full-page app loading, dashboard loading, route-level loading |
| `emptyData` | `https://lottie.host/c482328b-86c2-44b3-b346-044ae579d74a/0Dn0NfqGBk.lottie` | Generic empty states for tables, cards, notifications, audit-style empties |
| `emptyProducts` | `https://lottie.host/6471e2a1-a6ef-4ef3-8fd0-4324c0dbc4d7/ntgJhyeQf4.lottie` | Products list empty state |
| `emptyCustomers` | `https://lottie.host/74b4de10-1990-4c72-b753-e9462b7b498e/mfF9q0k61O.lottie` | Customers list empty state |
| `emptyVendors` | `https://lottie.host/74b4de10-1990-4c72-b753-e9462b7b498e/mfF9q0k61O.lottie` | Vendors list empty state |
| `emptySalesOrders` | `https://lottie.host/05726d8a-a59b-467f-b6eb-7e5ec5f3abf0/LN3KOMviRz.lottie` | Sales orders list empty state |
| `emptyPurchaseOrders` | `https://lottie.host/05726d8a-a59b-467f-b6eb-7e5ec5f3abf0/LN3KOMviRz.lottie` | Purchase orders list empty state |
| `emptyWarehouses` | `https://lottie.host/03c46c70-e8a5-416b-8172-4753dfc87822/USwrdK6Sg4.lottie` | Warehouses list empty state |
| `notFound404` | `https://lottie.host/5cbb50a5-9ca3-47f7-ab2d-1b31f43e5592/bjJuRG03wX.lottie` | 404 and not-found screens |
| `comingSoon` | `https://lottie.host/5eab4627-7fff-4bd8-9a66-19661ad8c85c/a9WVF4WqY5.lottie` | Future modules, placeholder surfaces, coming-soon screens |
| `onboarding` | `https://lottie.host/68f0986b-79a7-4926-be0f-e4c8464d78b9/GXgwKOPuC2.lottie` | Login/signup hero, onboarding, setup checklist, success-style onboarding surfaces |
| `financeReports` | `https://lottie.host/e6e1d594-8acd-46dc-88c2-caa932561f37/mBxEoWCb0K.lottie` | Reports hero, report workspace, subscription and plan usage screens |

## Where each animation is used

- `appLoading`
  - dashboard full-page loading
  - notifications loading
  - reports loading
  - subscription governance loading
- `emptyData`
  - generic `EmptyState`
  - notifications empty
  - no-report-rows state
  - generic list empty fallbacks
  - table error fallback styling
- `emptyProducts`
  - items list when no products exist
- `emptyCustomers`
  - customers list when no customers exist
- `emptyVendors`
  - vendors list when no vendors exist
- `emptySalesOrders`
  - sales orders list when no sales orders exist
- `emptyPurchaseOrders`
  - purchase orders list when no purchase orders exist
- `emptyWarehouses`
  - warehouses list when no warehouses exist
- `notFound404`
  - not found route page
- `comingSoon`
  - placeholder module screens
- `onboarding`
  - login hero
  - signup hero
  - onboarding / organization setup hero
  - success-style reusable state fallback
- `financeReports`
  - reports page header illustration
  - subscription plan catalog illustration
  - report filter error/loading contexts

## How to replace an animation URL later

1. Open [frontend/src/config/animations.js](/Users/as-mac-1293/Desktop/mini-zoho/frontend/src/config/animations.js)
2. Find the animation key you want to replace
3. Replace only the `src` value with a direct `.lottie` URL
4. Keep the key name unchanged so existing UI components continue to work

Example:

```js
emptyProducts: {
  label: "No Products",
  src: "https://your-new-direct-url.lottie",
  usage: "Products screen when no products exist",
}
```

## Notes

- The selected animations came from LottieFiles-hosted URLs.
- Verify licensing and commercial-use terms before production deployment.
- Do not paste raw `<script>` embed snippets into React pages.
- Use the reusable React component in [frontend/src/components/common/LottieAnimation.jsx](/Users/as-mac-1293/Desktop/mini-zoho/frontend/src/components/common/LottieAnimation.jsx) instead.
