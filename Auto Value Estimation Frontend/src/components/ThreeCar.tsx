import { useEffect, useRef } from "react";

declare global {
  interface Window {
    THREE: any;
  }
}
const ThreeCar = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let disposed = false;
    let cleanup: (() => void) | undefined;

    const init = () => {
      const THREE = (window as any).THREE;
      if (!THREE) {
        if (!disposed) setTimeout(init, 50);
        return;
      }

      const container = containerRef.current!;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
      camera.position.set(0.6, 1.25, 3.6);

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setClearColor(0x000000, 0);
      container.appendChild(renderer.domElement);
      renderer.domElement.style.width = "100%";
      renderer.domElement.style.height = "100%";

      // More realistic rendering
      renderer.physicallyCorrectLights = true;
      if (renderer.toneMapping !== undefined) {
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.15;
      }
      if (renderer.outputColorSpace !== undefined) {
        renderer.outputColorSpace = THREE.SRGBColorSpace;
      }
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;

      // Ensure a visible backdrop if nothing else shows
      // scene.background = new THREE.Color(0x0b0f1a);

      const resize = () => {
        const parent = container.parentElement as HTMLElement | null;
        const w = container.clientWidth || parent?.clientWidth || window.innerWidth;
        const h = container.clientHeight || parent?.clientHeight || 600;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h, false);
      };
      resize();
      // If first layout is 0 height, try again on next frame
      if ((container.clientHeight || 0) === 0) {
        requestAnimationFrame(resize);
      }
      window.addEventListener("resize", resize);

      // Lights
      const ambient = new THREE.AmbientLight(0xffffff, 0.25);
      scene.add(ambient);
      const spot = new THREE.SpotLight(0xffffff, 2.2, 15, Math.PI / 6, 0.3, 1.5);
      spot.position.set(2.8, 5.2, 3.2);
      spot.castShadow = true;
      spot.shadow.mapSize.set(1024, 1024);
      spot.shadow.bias = -0.0002;
      scene.add(spot);
      const fill = new THREE.DirectionalLight(0x7fb3ff, 0.5);
      fill.position.set(-3, 2.5, -2);
      scene.add(fill);

      // Ground shadow catcher
      const ground = new THREE.Mesh(
        new THREE.PlaneGeometry(30, 30),
        new THREE.ShadowMaterial({ opacity: 0.25 })
      );
      ground.receiveShadow = true;
      ground.rotation.x = -Math.PI / 2;
      ground.position.y = 0;
      scene.add(ground);

      // Car group (will hold either primitive or GLTF model)
      const car = new THREE.Group();
      scene.add(car);

      const bodyMat = new THREE.MeshPhysicalMaterial({ color: 0x1f3a8a, metalness: 0.95, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.08, reflectivity: 1 });
      const darkMat = new THREE.MeshStandardMaterial({ color: 0x0e1116, metalness: 0.2, roughness: 0.75 });
      const rubberMat = new THREE.MeshStandardMaterial({ color: 0x0b0b0b, metalness: 0.1, roughness: 0.9 });
      const rimMat = new THREE.MeshStandardMaterial({ color: 0xb0b7c3, metalness: 1, roughness: 0.3 });
      const brakeMat = new THREE.MeshStandardMaterial({ color: 0x9ca3af, metalness: 0.6, roughness: 0.5 });
      const glassMat = new THREE.MeshPhysicalMaterial({ color: 0x9ec6ff, metalness: 0, roughness: 0.03, transmission: 0.7, transparent: true, opacity: 0.9, ior: 1.45, thickness: 0.5 });

      // Primitive placeholder car (used until GLTF loads)
      const primitives: any[] = [];
      // Rounded body using capsule-like shapes for smoother silhouette
      const body = new THREE.Mesh(new THREE.CapsuleGeometry(1.25, 1.0, 8, 24), bodyMat);
      body.scale.set(2.1, 0.32, 0.55);
      body.position.y = 0.72;
      body.castShadow = true; car.add(body); primitives.push(body);

      const cabin = new THREE.Mesh(new THREE.CapsuleGeometry(0.9, 0.4, 8, 16), glassMat);
      cabin.scale.set(1.2, 0.42, 0.72);
      cabin.position.set(0.15, 1.05, 0);
      cabin.castShadow = true; car.add(cabin); primitives.push(cabin);

      const hood = new THREE.Mesh(new THREE.CapsuleGeometry(0.55, 0.2, 8, 16), bodyMat);
      hood.scale.set(1.4, 0.6, 0.95);
      hood.position.set(-1.05, 0.92, 0);
      hood.castShadow = true; car.add(hood); primitives.push(hood);

      const trunk = new THREE.Mesh(new THREE.CapsuleGeometry(0.5, 0.2, 8, 16), bodyMat);
      trunk.scale.set(1.1, 0.6, 0.95);
      trunk.position.set(1.1, 0.92, 0);
      trunk.castShadow = true; car.add(trunk); primitives.push(trunk);

      const tyreGeo = new THREE.TorusGeometry(0.36, 0.09, 16, 28);
      const rimGeo = new THREE.CylinderGeometry(0.26, 0.26, 0.06, 24);
      rimGeo.rotateZ(Math.PI / 2);
      const brakeGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.02, 24);
      brakeGeo.rotateZ(Math.PI / 2);

      const addWheel = (x: number, z: number) => {
        const group = new THREE.Group();
        const tyre = new THREE.Mesh(tyreGeo, rubberMat);
        const rim = new THREE.Mesh(rimGeo, rimMat);
        const brake = new THREE.Mesh(brakeGeo, brakeMat);
        tyre.castShadow = true; rim.castShadow = true;
        group.add(tyre, rim, brake);
        group.position.set(x, 0.34, z);
        car.add(group);
        primitives.push(group);
        return group;
      };
      const wfl = addWheel(-1.0, 0.6);
      const wfr = addWheel(-1.0, -0.6);
      const wrl = addWheel(1.0, 0.6);
      const wrr = addWheel(1.0, -0.6);

      // Ground shadow
      // Faint blob shadow (in addition to real shadows)
      const shadow = new THREE.Mesh(
        new THREE.CircleGeometry(1.6, 32).rotateX(-Math.PI / 2),
        new THREE.MeshBasicMaterial({ color: 0x0b1220, transparent: true, opacity: 0.12 })
      );
      shadow.position.y = 0.005;
      scene.add(shadow);

      // Cursor-based orbit + idle animation
      let targetRotY = 0; // user target yaw
      let targetRotX = -0.1; // user target pitch
      let mouseActive = false;
      const onMove = (e: MouseEvent) => {
        const rect = container.getBoundingClientRect();
        const nx = (e.clientX - rect.left) / rect.width; // 0..1
        const ny = (e.clientY - rect.top) / rect.height; // 0..1
        targetRotY = (nx - 0.5) * 0.9; // left-right
        targetRotX = -0.15 + (0.5 - ny) * 0.2; // up-down
      };
      const onEnter = () => { mouseActive = true; };
      const onLeave = () => { mouseActive = false; };
      container.addEventListener("mousemove", onMove);
      container.addEventListener("mouseenter", onEnter);
      container.addEventListener("mouseleave", onLeave);

      let raf: number;
      let t0 = performance.now();
      let mixer: any | undefined;
      const tick = () => {
        const now = performance.now();
        const t = (now - t0) / 1000; // seconds since start
        // Smooth follow
        // Idle auto-rotation when mouse not active
        const idleYaw = Math.sin(t * 0.25) * 0.25; // slow sway left/right
        const idlePitch = -0.12 + Math.sin(t * 0.18 + 1.2) * 0.04; // gentle pitch
        const desiredY = mouseActive ? targetRotY : idleYaw;
        const desiredX = mouseActive ? targetRotX : idlePitch;
        car.rotation.y += (desiredY - car.rotation.y) * 0.08;
        car.rotation.x += (desiredX - car.rotation.x) * 0.08;

        // Slow auto movement and bobbing
        car.position.x = Math.sin(t * 0.35) * 0.2; // subtle left/right drift
        car.position.y = 0.02 + Math.sin(t * 1.2) * 0.02; // subtle bob

        // Wheels gentle spin (placeholder)
        const spin = 0.06 + Math.abs(Math.sin(t * 0.4)) * 0.015;
        if (wfl) wfl.rotation.x += spin;
        if (wfr) wfr.rotation.x += spin;
        if (wrl) wrl.rotation.x += spin;
        if (wrr) wrr.rotation.x += spin;

        // Animate GLTF if it has animations
        if (mixer) mixer.update(1/60);

        renderer.render(scene, camera);
        raf = requestAnimationFrame(tick);
      };
      tick();

      cleanup = () => {
        cancelAnimationFrame(raf);
        container.removeEventListener("mousemove", onMove);
        container.removeEventListener("mouseenter", onEnter);
        container.removeEventListener("mouseleave", onLeave);
        window.removeEventListener("resize", resize);
        renderer.dispose();
        while (container.firstChild) {
          container.removeChild(container.firstChild);
        }
      };

      // Try loading a GLTF/GLB from public URLs first (no auth required),
      // then fall back to local /public paths if available.
      const urlModel = new URLSearchParams(window.location.search).get("model") || undefined;
      const tryPaths = [
        // If a model query param is provided, try that first
        ...(urlModel ? [urlModel] : []),
        // Public Lamborghini Aventador (gltf + external textures) hosted on GitHub raw
        "https://raw.githubusercontent.com/aaronbernath143/3D-car-model/master/data/aventador/scene.gltf",
        // Public car models (Khronos glTF sample models, permissive and CORS-enabled)
        "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Buggy/glTF-Binary/Buggy.glb",
        "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/ToyCar/glTF-Binary/ToyCar.glb",
        // Local paths (if you later add models under /public)
        "/model/aventador.glb",
        "/model/aventador/scene.gltf",
        "/model/car.glb",
        "/model/scene.gltf",
        "/model/scene.glb",
        "/models/car.glb",
        "/models/scene.gltf",
      ];
      const GLTFLoader = (THREE as any).GLTFLoader;
      if (GLTFLoader) {
        const loader = new GLTFLoader();
        const DRACOLoader = (THREE as any).DRACOLoader;
        if (DRACOLoader) {
          const draco = new DRACOLoader();
          draco.setDecoderPath("https://unpkg.com/three@0.160.0/examples/js/libs/draco/");
          loader.setDRACOLoader(draco);
        }
        const loadNext = (idx: number) => {
          if (idx >= tryPaths.length) return; // keep primitives
          loader.load(
            tryPaths[idx],
            (gltf: any) => {
              // Remove primitives
              primitives.forEach((m) => car.remove(m));
              // Add loaded scene
              const model = gltf.scene;
              model.traverse((o: any) => {
                if (o.isMesh) {
                  o.castShadow = true; o.receiveShadow = true;
                  if (o.material) {
                    // Force car-paint like material for exterior-looking meshes
                    const name = (o.name || "").toLowerCase();
                    if (name.includes("body") || name.includes("paint") || name.includes("car") || name.includes("exterior")) {
                      o.material = new THREE.MeshPhysicalMaterial({
                        color: 0xc8102e, metalness: 1, roughness: 0.18,
                        clearcoat: 1, clearcoatRoughness: 0.06,
                        reflectivity: 1
                      });
                    } else if (name.includes("glass") || name.includes("window") || name.includes("windscreen")) {
                      o.material = new THREE.MeshPhysicalMaterial({
                        color: 0x9ec6ff, metalness: 0, roughness: 0.03,
                        transmission: 0.75, transparent: true, opacity: 0.9, ior: 1.45, thickness: 0.6
                      });
                    }
                  }
                }
              });
              // Fit camera to model bounds & set hero-friendly presentation
              const box = new THREE.Box3().setFromObject(model);
              const size = box.getSize(new THREE.Vector3());
              const center = box.getCenter(new THREE.Vector3());
              const maxDim = Math.max(size.x, size.y, size.z);
              const fitDist = (maxDim / (2 * Math.tan((Math.PI * camera.fov) / 360)));
              const target = new THREE.Vector3(center.x, center.y * 0.6, center.z);
              camera.position.copy(target.clone().add(new THREE.Vector3(0.9, 0.55, fitDist * 1.25)));
              camera.lookAt(target);
              model.position.sub(center); // center on origin
              model.position.y += 0.35;
              model.rotation.y = Math.PI * 0.15;
              const s = 1.2 * (1.6 / maxDim);
              model.scale.setScalar(s);
              car.add(model);

              // Animations if present
              if (gltf.animations && gltf.animations.length) {
                mixer = new THREE.AnimationMixer(model);
                gltf.animations.forEach((clip: any) => mixer!.clipAction(clip).play());
              }
            },
            undefined,
            () => loadNext(idx + 1)
          );
        };
        loadNext(0);
      }

      // Environment map (HDR) for realistic reflections
      const RGBELoader = (THREE as any).RGBELoader;
      if (RGBELoader) {
        const rgbe = new RGBELoader();
        rgbe.setDataType(THREE.UnsignedByteType).load(
          "https://cdn.jsdelivr.net/gh/mrdoob/three.js@r160/examples/textures/equirectangular/venice_sunset_1k.hdr",
          (hdr: any) => {
            const pmrem = new THREE.PMREMGenerator(renderer);
            pmrem.compileEquirectangularShader();
            const envMap = pmrem.fromEquirectangular(hdr).texture;
            scene.environment = envMap;
            hdr.dispose?.();
            pmrem.dispose();
          }
        );
      }
    };

    init();

    return () => {
      disposed = true;
      if (cleanup) cleanup();
    };
  }, []);

  return <div ref={containerRef} className="absolute inset-0" style={{ zIndex: 1 }} />;
};

export default ThreeCar;


