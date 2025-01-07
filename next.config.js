/** @type {import('next').NextConfig} */
const nextConfig = {
  serverActions: {
    bodySizeLimit: '50mb' // หรือขนาดที่ต้องการ เช่น '10mb'
  }
}

module.exports = nextConfig 