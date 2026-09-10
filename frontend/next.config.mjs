/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Node 22+ on Windows crashes Next 14's threaded prerender worker (exit 0xC0000409); use processes.
  experimental: { workerThreads: false, cpus: 1 },
  async rewrites() {
    // Lets the browser call /api/* same-origin during local dev; production points NEXT_PUBLIC_API_URL at the API host.
    const target = process.env.API_PROXY_TARGET;
    return target
      ? [{ source: "/api/:path*", destination: `${target}/:path*` }]
      : [];
  },
};

export default nextConfig;
