import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Hero, About, Courses, Team, Gallery, Certifications, TechTools, Contact } from "@/components/Sections";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      <Courses />
      <About />
      <Team />
      <Gallery />
      <Certifications />
      <TechTools />
      <Contact />
      <Footer />
    </div>
  );
};

export default Index;
