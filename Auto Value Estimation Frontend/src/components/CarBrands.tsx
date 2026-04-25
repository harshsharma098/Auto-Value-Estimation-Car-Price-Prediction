import { Car } from "lucide-react";

type Brand = { name: string; image: string };

// Using reliable image URLs (Wikimedia/press/stock). Replace with local assets if preferred.
const brands: Brand[] = [
  {
    name: "Maruti Suzuki",
    image:
      "https://stimg.cardekho.com/images/carexteriorimages/930x620/Maruti/Dzire/11387/1758802554630/front-left-side-47.jpg",
  },
  {
    name: "Hyundai",
    image:
      "https://etimg.etb2bimg.com/photo/109522069.cms",
  },
  {
    name: "Tata",
    image:
      "https://imgd.aeplcdn.com/1280x720/n/cw/ec/159551/tata-safari-facelift-right-front-three-quarter2.jpeg?isig=0",
  },
  {
    name: "Mahindra",
    image:
      "https://c.ndtvimg.com/2024-10/phm1qec_mahindrascorpioclassicbossedition1_625x300_23_October_24.jpg?im=FeatureCrop,algorithm=dnn,width=1200,height=738",
  },
  {
    name: "Honda",
    image:
      "https://v3cars.com/media/model-imgs/1677750961-2023-city-facelift.webp",
  },
  {
    name: "Toyota",
    image:
      "https://imgd.aeplcdn.com/664x374/n/cw/ec/137767/fortuner-legender-exterior-right-front-three-quarter-5.png?isig=0&q=80",
  },
  {
    name: "Ford",
    image:
      "https://images.financialexpressdigital.com/2020/02/Ford-Endeavour-bs6.jpg",
  },
  {
    name: "Renault",
    image:
      "https://imgd.aeplcdn.com/664x374/n/cw/ec/47028/duster-exterior-right-front-three-quarter-4.jpeg?q=80",
  },
];

const CarBrands = () => {
  return (
    <section className="py-12 bg-muted/30">
      <div className="container mx-auto px-4">
        <h2 className="text-2xl font-bold text-center mb-8 text-foreground">
          We Value All Major Brands
        </h2>
        {/* Auto-scrolling marquee of brands */}
        <div className="marquee-viewport">
          <div className="marquee-track">
            {[...brands, ...brands].map((brand, idx) => (
              <div
                key={`${brand.name}-${idx}`}
                className="flex flex-col items-center justify-center p-4 bg-card rounded-lg border border-border hover:border-primary transition-all duration-300 hover:shadow-md cursor-pointer group min-w-[180px]"
              >
                <div className="w-[160px] h-[100px] mb-3 overflow-hidden rounded-md bg-muted/50 flex items-center justify-center">
                  {brand.image ? (
                    <img
                      src={brand.image}
                      alt={`${brand.name} car`}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.05]"
                      loading="lazy"
                      referrerPolicy="no-referrer"
                    />
                  ) : (
                    <div className="bg-primary/10 p-3 rounded-full">
                      <Car className="h-6 w-6 text-primary" />
                    </div>
                  )}
                </div>
                <span className="text-xs font-medium text-center text-foreground">{brand.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default CarBrands;
