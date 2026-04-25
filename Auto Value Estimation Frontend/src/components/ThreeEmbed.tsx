const ThreeEmbed = () => {
  return (
    <iframe
      src="https://codesandbox.io/embed/578s68?view=preview&module=%2Findex.html"
      title="car-3d-embed"
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        border: 0,
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: 1,
      }}
      allow="accelerometer; ambient-light-sensor; camera; encrypted-media; geolocation; gyroscope; hid; microphone; midi; payment; usb; vr; xr-spatial-tracking"
      sandbox="allow-forms allow-modals allow-popups allow-presentation allow-same-origin allow-scripts"
    />
  );
};

export default ThreeEmbed;


