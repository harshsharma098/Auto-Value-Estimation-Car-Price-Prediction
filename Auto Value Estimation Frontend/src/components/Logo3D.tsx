type Props = { title?: string };

const Logo3D = ({ title = "AutoValue" }: Props) => {
  return (
    <div className="relative flex items-center gap-3 select-none">
      {/* Emblem */}
      <div className="relative h-10 w-10">
        <svg viewBox="0 0 64 64" className="h-full w-full drop-shadow-[0_8px_18px_rgba(16,16,16,0.35)]">
          <defs>
            <linearGradient id="grad1" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="hsl(16 100% 60%)" />
              <stop offset="100%" stopColor="hsl(24 100% 58%)" />
            </linearGradient>
            <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fff" stopOpacity=".9" />
              <stop offset="100%" stopColor="#aab4c3" stopOpacity=".9" />
            </linearGradient>
          </defs>
          {/* Shield */}
          <path d="M32 4c8 6 16 6 24 4v22c0 14-10 26-24 30C18 56 8 44 8 30V8c8 2 16 2 24-4z" fill="url(#grad1)"/>
          {/* Car silhouette */}
          <path d="M13 30c6-5 14-7 23-7 9 0 16 2 22 7-1 3-2 4-4 4H17c-2 0-3-1-4-4z" fill="url(#metal)" opacity=".9"/>
          {/* Shine */}
          <path d="M10 18c10-2 20-4 30-11" stroke="#fff" strokeOpacity=".5" strokeWidth="3" fill="none"/>
        </svg>
        {/* subtle top gloss */}
        <div className="absolute inset-0 rounded-xl bg-[linear-gradient(180deg,rgba(255,255,255,.25),transparent_40%)] pointer-events-none" />
      </div>
      {/* Wordmark with depth */}
      <div className="leading-none font-extrabold tracking-tight">
        <span className="logo-3d-text text-2xl md:text-3xl">{title}</span>
      </div>
    </div>
  );
};

export default Logo3D;


