import { Button } from "@/components/ui/button";
import { BookOpen, Menu, X } from "lucide-react";
import { useState } from "react";

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    element?.scrollIntoView({ behavior: "smooth" });
    setIsOpen(false);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <BookOpen className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold text-foreground">CEAMA</span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <button
              onClick={() => scrollToSection("inicio")}
              className="text-foreground hover:text-primary transition-colors"
            >
              Inicio
            </button>
            <button
              onClick={() => scrollToSection("cursos")}
              className="text-foreground hover:text-primary transition-colors"
            >
              Cursos
            </button>
            <button
              onClick={() => scrollToSection("nosotros")}
              className="text-foreground hover:text-primary transition-colors"
            >
              Nosotros
            </button>
            <button
              onClick={() => scrollToSection("conocenos")}
              className="text-foreground hover:text-primary transition-colors"
            >
              Conócenos
            </button>
            <button
              onClick={() => scrollToSection("galeria")}
              className="text-foreground hover:text-primary transition-colors"
            >
              Galería
            </button>
            <button
              onClick={() => scrollToSection("contacto")}
              className="text-foreground hover:text-primary transition-colors"
            >
              Contacto
            </button>
            <Button variant="outline" onClick={() => scrollToSection("contacto")}>
              Regularización de Pagos
            </Button>
            <Button>Inscríbete Ahora</Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-foreground"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 space-y-4">
            <button
              onClick={() => scrollToSection("inicio")}
              className="block w-full text-left text-foreground hover:text-primary transition-colors py-2"
            >
              Inicio
            </button>
            <button
              onClick={() => scrollToSection("cursos")}
              className="block w-full text-left text-foreground hover:text-primary transition-colors py-2"
            >
              Cursos
            </button>
            <button
              onClick={() => scrollToSection("nosotros")}
              className="block w-full text-left text-foreground hover:text-primary transition-colors py-2"
            >
              Nosotros
            </button>
            <button
              onClick={() => scrollToSection("conocenos")}
              className="block w-full text-left text-foreground hover:text-primary transition-colors py-2"
            >
              Conócenos
            </button>
            <button
              onClick={() => scrollToSection("galeria")}
              className="block w-full text-left text-foreground hover:text-primary transition-colors py-2"
            >
              Galería
            </button>
            <button
              onClick={() => scrollToSection("contacto")}
              className="block w-full text-left text-foreground hover:text-primary transition-colors py-2"
            >
              Contacto
            </button>
            <Button variant="outline" className="w-full mb-2" onClick={() => scrollToSection("contacto")}>
              Regularización de Pagos
            </Button>
            <Button className="w-full">Inscríbete Ahora</Button>
          </div>
        )}
      </div>
    </nav>
  );
};
