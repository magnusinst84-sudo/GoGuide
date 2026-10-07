import "./globals.css";

export const metadata = {
  title: "GoGuide",
  description: "AI-powered education and career guidance for students and families.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}
