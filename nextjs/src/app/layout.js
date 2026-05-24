import "bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";
import Script from "next/script";
import { AuthProvider } from "./context/AuthContext";

const BOOTSTRAP_BUNDLE_SRC =
  "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js";
const BOOTSTRAP_INTEGRITY =
  "sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
          <Script
            src={BOOTSTRAP_BUNDLE_SRC}
            integrity={BOOTSTRAP_INTEGRITY}
            crossOrigin="anonymous"
            strategy="afterInteractive"
          />
        </AuthProvider>
      </body>
    </html>
  );
}
