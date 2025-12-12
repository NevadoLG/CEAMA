import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import {
  Target,
  Users,
  Award,
  BookOpen,
  CheckCircle2,
  Mail,
  Phone,
  MapPin,
  Clock,
  ArrowRight,
  X,
  Brain,
  Video,
  Gamepad2,
  BookText,
  Sparkles,
  Trophy,
} from "lucide-react";

// Import assets
import classroomBg from "@/assets/classroom-bg.png";
import communicationIcon from "@/assets/communication-icon.jpg";
import mathIcon from "@/assets/math-icon.jpg";
import physicsIcon from "@/assets/physics-icon.jpg";
import coursesBg from "@/assets/courses-bg.jpg";
import teacherProfile from "@/assets/teacher-profile-new.png";
import kahootVerified from "@/assets/kahoot-verified.png";
import teacherDiana from "@/assets/teacher-diana.png";
import teacherLiliana from "@/assets/teacher-liliana.png";
import teacherGiovanna from "@/assets/teacher-giovanna.png";
import teacherClass1 from "@/assets/gallery/teacher-class-1.png";
import communicationClass from "@/assets/gallery/communication-class.jpg";
import mathClass from "@/assets/gallery/math-class.jpg";
import groupClass1 from "@/assets/gallery/group-class-1.jpg";
import groupClass2 from "@/assets/gallery/group-class-2.jpg";
import teacherClass2 from "@/assets/gallery/teacher-class-2.jpg";
import groupClass3 from "@/assets/gallery/group-class-3.jpg";
import certificationsBg from "@/assets/certifications-bg.jpg";
import techtoolsBg from "@/assets/techtools-bg.jpg";
import contactBg from "@/assets/contact-bg.jpg";

// Hero Section
export const Hero = () => {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    element?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="inicio"
      className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16"
    >
      <div className="absolute inset-0 z-0">
        <img
          src={classroomBg}
          alt="CEAMA Academia Classroom"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-primary/90 to-primary/70"></div>
      </div>

      <div className="container mx-auto px-4 z-10 text-center">
        <div className="max-w-4xl mx-auto space-y-6">
          <h1 className="text-5xl md:text-7xl font-bold text-primary-foreground animate-fade-in">
            Bienvenido a CEAMA
          </h1>
          <p className="text-xl md:text-2xl text-primary-foreground/90 max-w-2xl mx-auto">
            Centro de Excelencia Académica en Matemática y Comunicación
          </p>
          <p className="text-lg md:text-xl text-primary-foreground/80 max-w-3xl mx-auto">
            Desarrollamos habilidades esenciales para el éxito académico y
            profesional a través de programas especializados en comunicación
            efectiva y razonamiento matemático.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
            <Button
              size="lg"
              variant="secondary"
              onClick={() => scrollToSection("cursos")}
              className="text-lg"
            >
              Ver Cursos
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => scrollToSection("contacto")}
              className="text-lg bg-transparent border-2 border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary"
            >
              Contáctanos
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

// About Section
export const About = () => {
  const features = [
    {
      icon: Target,
      title: "Metodología Efectiva",
      description:
        "Aplicamos técnicas pedagógicas innovadoras que garantizan el aprendizaje significativo y duradero.",
    },
    {
      icon: Users,
      title: "Docentes Expertos",
      description:
        "Nuestro equipo está conformado por profesionales altamente calificados con amplia experiencia educativa.",
    },
    {
      icon: Award,
      title: "Resultados Comprobados",
      description:
        "Miles de estudiantes han logrado sus objetivos académicos gracias a nuestros programas de estudio.",
    },
    {
      icon: BookOpen,
      title: "Material Didáctico",
      description:
        "Proporcionamos recursos educativos de calidad diseñados específicamente para cada nivel y necesidad.",
    },
  ];

  return (
    <section id="nosotros" className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            ¿Por Qué Elegirnos?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Somos una institución comprometida con la excelencia académica y el
            desarrollo integral de nuestros estudiantes
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="text-center hover:shadow-lg transition-shadow"
            >
              <CardContent className="pt-6 space-y-4">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10">
                  <feature.icon className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-16 max-w-4xl mx-auto bg-gradient-to-r from-primary/10 to-education-secondary/10 rounded-lg p-8">
          <h3 className="text-2xl font-bold text-foreground mb-4 text-center">
            Nuestra Misión
          </h3>
          <p className="text-lg text-muted-foreground text-center leading-relaxed">
            En CEAMA nos dedicamos a formar estudiantes con sólidas competencias
            en comunicación y matemática, brindándoles las herramientas
            necesarias para destacar en su vida académica y profesional.
            Creemos en la educación de calidad como el camino hacia el éxito y
            el desarrollo personal.
          </p>
        </div>
      </div>
    </section>
  );
};

// Courses Section
export const Courses = () => {
  return (
    <section id="cursos" className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img
          src={coursesBg}
          alt="Cursos background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-warm opacity-80"></div>
      </div>
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Nuestros Cursos
          </h2>
          <p className="text-lg text-white/90 max-w-2xl mx-auto">
            Programas diseñados especialmente para que aprendas de forma
            divertida y efectiva
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Card className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:scale-105 bg-white/95 backdrop-blur-sm">
            <div className="h-48 overflow-hidden bg-gradient-to-br from-education-orange to-education-yellow">
              <img
                src={communicationIcon}
                alt="Curso de Comunicación"
                className="w-full h-full object-cover opacity-90"
              />
            </div>
            <CardHeader>
              <CardTitle className="text-2xl">Comunicación</CardTitle>
              <CardDescription className="text-base">
                Aprende a leer, escribir y expresarte mejor
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Mejora tu lectura, escritura y forma de hablar de manera divertida y práctica.
              </p>
              <ul className="space-y-2">
                {[
                  "Lectura comprensiva y entretenida",
                  "Redacción de textos sencillos",
                  "Expresión oral con confianza",
                  "Ortografía y gramática básica",
                  "Cuentos y narraciones",
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-education-primary shrink-0 mt-0.5" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:scale-105 bg-white/95 backdrop-blur-sm">
            <div className="h-48 overflow-hidden bg-gradient-to-br from-education-primary to-education-teal">
              <img
                src={mathIcon}
                alt="Curso de Matemática"
                className="w-full h-full object-cover opacity-90"
              />
            </div>
            <CardHeader>
              <CardTitle className="text-2xl">Matemática</CardTitle>
              <CardDescription className="text-base">
                Aprende matemáticas de forma divertida
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Resuelve problemas matemáticos con técnicas sencillas y juegos entretenidos.
              </p>
              <ul className="space-y-2">
                {[
                  "Operaciones básicas y mental",
                  "Problemas de razonamiento lógico",
                  "Geometría con figuras y formas",
                  "Juegos matemáticos",
                  "Fracciones y números decimales",
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-education-secondary shrink-0 mt-0.5" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:scale-105 bg-white/95 backdrop-blur-sm">
            <div className="h-48 overflow-hidden bg-gradient-to-br from-education-purple to-education-coral">
              <img
                src={physicsIcon}
                alt="Curso de Física"
                className="w-full h-full object-cover opacity-90"
              />
            </div>
            <CardHeader>
              <CardTitle className="text-2xl">Física</CardTitle>
              <CardDescription className="text-base">
                Descubre cómo funciona el mundo que te rodea
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Explora la ciencia de manera práctica con experimentos simples y conceptos básicos.
              </p>
              <ul className="space-y-2">
                {[
                  "Fuerzas y movimiento",
                  "Energía y sus formas",
                  "Luz y sonido",
                  "Experimentos sencillos",
                  "Máquinas simples",
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-education-accent shrink-0 mt-0.5" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

// Team Section
export const Team = () => {
  return (
    <section id="conocenos" className="py-20 bg-gradient-to-br from-education-teal/20 to-education-purple/20 relative overflow-hidden">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Conócenos
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Nuestro equipo docente altamente calificado
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div className="relative">
              <div className="rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src={teacherProfile}
                  alt="Profesor CEAMA"
                  className="w-full h-auto object-cover"
                />
              </div>
              <div className="absolute -bottom-4 -right-4 bg-white rounded-full p-4 shadow-xl">
                <img
                  src={kahootVerified}
                  alt="Kahoot Verified Creator"
                  className="w-20 h-20 object-contain"
                />
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-3xl font-bold text-foreground mb-2">
                  [Nombre del Profesor]
                </h3>
                <p className="text-xl text-muted-foreground mb-4">
                  Director y Profesor Principal
                </p>
              </div>

              <Card className="bg-gradient-to-br from-education-teal to-education-primary border-0">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-3">
                    <img
                      src={kahootVerified}
                      alt="Kahoot Verified"
                      className="w-12 h-12"
                    />
                    <div>
                      <h4 className="text-white font-bold text-lg">
                        Kahoot! Verified Creator
                      </h4>
                      <p className="text-white/90 text-sm">
                        Creador verificado oficial
                      </p>
                    </div>
                  </div>
                  <p className="text-white/90">
                    Reconocido por Kahoot! por crear contenido educativo de alta calidad 
                    e innovador que impacta positivamente en el aprendizaje de estudiantes.
                  </p>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 gap-4">
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-4 flex items-start gap-3">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-education-orange to-education-yellow flex-shrink-0">
                      <BookOpen className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-foreground mb-1">
                        Más de 25 años de experiencia
                      </h5>
                      <p className="text-sm text-muted-foreground">
                        Especializado en matemática para nivel primaria y secundaria - Colegio San José Obrero
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-4 flex items-start gap-3">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-education-purple to-education-coral flex-shrink-0">
                      <Award className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-foreground mb-1">
                        Metodología Innovadora
                      </h5>
                      <p className="text-sm text-muted-foreground">
                        Aplicando técnicas pedagógicas modernas y tecnología educativa
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-4 flex items-start gap-3">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-education-teal to-education-secondary flex-shrink-0">
                      <Users className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-foreground mb-1">
                        Compromiso con el estudiante
                      </h5>
                      <p className="text-sm text-muted-foreground">
                        Enfoque personalizado para el éxito de cada alumno
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>

          <div className="mt-16">
            <h3 className="text-3xl font-bold text-center text-foreground mb-8">
              Nuestro Equipo Docente
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="hover:shadow-xl transition-all">
                <CardContent className="p-6 text-center">
                  <div className="flex flex-col items-center">
                    <div className="w-32 h-32 rounded-full overflow-hidden mb-4 border-4 border-education-teal shadow-lg">
                      <img
                        src={teacherLiliana}
                        alt="Liliana Alvarez Chavez"
                        className="w-full h-full object-cover object-top"
                      />
                    </div>
                    <h4 className="text-xl font-bold text-foreground mb-2">
                      Liliana Alvarez Chavez
                    </h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      Docente especialista 1ro. y 2do. grado primaria
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Colegio Rafael Narvaez Cadenillas
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card className="hover:shadow-xl transition-all">
                <CardContent className="p-6 text-center">
                  <div className="flex flex-col items-center">
                    <div className="w-32 h-32 rounded-full overflow-hidden mb-4 border-4 border-education-purple shadow-lg">
                      <img
                        src={teacherDiana}
                        alt="Diana Castillo Miñano"
                        className="w-full h-full object-cover object-top"
                      />
                    </div>
                    <h4 className="text-xl font-bold text-foreground mb-2">
                      Diana Castillo Miñano
                    </h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      Docente especialista en el área de Comunicación
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Colegio Rafael Narvaez Cadenillas
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card className="hover:shadow-xl transition-all">
                <CardContent className="p-6 text-center">
                  <div className="flex flex-col items-center">
                    <div className="w-32 h-32 rounded-full overflow-hidden mb-4 border-4 border-education-coral shadow-lg">
                      <img
                        src={teacherGiovanna}
                        alt="Giovanna Tejada Suarez"
                        className="w-full h-full object-cover object-top"
                      />
                    </div>
                    <h4 className="text-xl font-bold text-foreground mb-2">
                      Giovanna Tejada Suarez
                    </h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      Docente especialista en primaria
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Colegio Rafael Narvaez Cadenillas
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Gallery Section
export const Gallery = () => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const images = [
    { src: teacherClass1, alt: "Clase con el profesor" },
    { src: communicationClass, alt: "Clase de Comunicación" },
    { src: mathClass, alt: "Clase de Matemática" },
    { src: groupClass1, alt: "Estudiantes en clase" },
    { src: groupClass2, alt: "Trabajo en grupo" },
    { src: teacherClass2, alt: "Enseñanza activa" },
    { src: groupClass3, alt: "Ambiente de aprendizaje" },
  ];

  return (
    <section id="galeria" className="py-20 bg-gradient-to-br from-education-primary/10 to-education-teal/10">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Galería
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Conoce nuestras instalaciones y el ambiente de aprendizaje que ofrecemos
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 max-w-7xl mx-auto">
          {images.map((image, index) => (
            <div
              key={index}
              className="relative overflow-hidden rounded-lg shadow-lg cursor-pointer group hover:scale-105 transition-transform duration-300"
              onClick={() => setSelectedImage(image.src)}
            >
              <img
                src={image.src}
                alt={image.alt}
                className="w-full h-64 object-cover group-hover:brightness-110 transition-all duration-300"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
          ))}
        </div>

        {selectedImage && (
          <div
            className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedImage(null)}
          >
            <button
              className="absolute top-4 right-4 text-white hover:text-gray-300 transition-colors"
              onClick={() => setSelectedImage(null)}
            >
              <X className="w-8 h-8" />
            </button>
            <img
              src={selectedImage}
              alt="Vista ampliada"
              className="max-w-full max-h-full object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        )}
      </div>
    </section>
  );
};

// Certifications Section
export const Certifications = () => {
  const certifications = [
    {
      title: "Kahoot Verified Creator",
      description:
        "Nuestros profesores son creadores verificados de Kahoot, reconocidos por crear contenido educativo de alta calidad.",
      badge: kahootVerified,
    },
    {
      title: "Experiencia Docente",
      description:
        "Equipo con más de 10 años de experiencia en enseñanza de matemática y comunicación.",
      icon: Users,
    },
    {
      title: "Metodología Certificada",
      description:
        "Aplicamos técnicas pedagógicas avaladas y probadas que garantizan resultados efectivos.",
      icon: CheckCircle2,
    },
    {
      title: "Reconocimiento Académico",
      description:
        "Premiados por excelencia en formación académica y metodología innovadora.",
      icon: Trophy,
    },
  ];

  return (
    <section id="certificaciones" className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img
          src={certificationsBg}
          alt="Certificaciones background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-teal opacity-85"></div>
      </div>
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Certificaciones y Reconocimientos
          </h2>
          <p className="text-lg text-white/90 max-w-2xl mx-auto">
            Respaldados por certificaciones profesionales y reconocimientos en
            excelencia educativa
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {certifications.map((cert, index) => (
            <Card
              key={index}
              className="text-center hover:shadow-xl transition-all duration-300 hover:scale-105 bg-white/95 backdrop-blur-sm"
            >
              <CardContent className="pt-6 space-y-4">
                {cert.badge ? (
                  <div className="flex justify-center">
                    <img
                      src={cert.badge}
                      alt={cert.title}
                      className="h-20 w-20 object-contain"
                    />
                  </div>
                ) : (
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-education-teal to-education-primary">
                    {cert.icon && <cert.icon className="h-8 w-8 text-white" />}
                  </div>
                )}
                <h3 className="text-xl font-semibold text-foreground">
                  {cert.title}
                </h3>
                <p className="text-muted-foreground text-sm">
                  {cert.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

// TechTools Section
export const TechTools = () => {
  const tools = [
    {
      icon: Brain,
      name: "Kahoot",
      description:
        "Cuestionarios interactivos que hacen del aprendizaje una experiencia divertida y competitiva.",
      color: "from-education-coral to-education-orange",
    },
    {
      icon: Sparkles,
      name: "Quizizz",
      description:
        "Evaluaciones gamificadas que motivan a los estudiantes a mejorar constantemente.",
      color: "from-education-purple to-education-primary",
    },
    {
      icon: Video,
      name: "Videos Dinámicos",
      description:
        "Contenido multimedia educativo diseñado para captar la atención y facilitar el aprendizaje.",
      color: "from-education-teal to-education-secondary",
    },
    {
      icon: BookText,
      name: "Materiales Físicos",
      description:
        "Libros de trabajo, fichas y recursos tangibles para complementar el aprendizaje digital.",
      color: "from-education-orange to-education-yellow",
    },
    {
      icon: Gamepad2,
      name: "Juegos Educativos",
      description:
        "Actividades lúdicas que refuerzan conceptos de manera práctica y entretenida.",
      color: "from-education-primary to-education-coral",
    },
  ];

  return (
    <section id="herramientas" className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img
          src={techtoolsBg}
          alt="Herramientas tecnológicas background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-coral opacity-85"></div>
      </div>
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Herramientas Tecnológicas
          </h2>
          <p className="text-lg text-white/90 max-w-2xl mx-auto">
            Utilizamos las mejores herramientas educativas para hacer el
            aprendizaje más efectivo y divertido
          </p>
        </div>

        <div className="max-w-5xl mx-auto">
          <Carousel
            opts={{
              align: "start",
              loop: true,
            }}
            className="w-full"
          >
            <CarouselContent>
              {tools.map((tool, index) => (
                <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/3">
                  <div className="p-1">
                    <Card className="overflow-hidden hover:shadow-xl transition-all duration-300 bg-white/95 backdrop-blur-sm">
                      <CardContent className="p-6 space-y-4">
                        <div
                          className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br ${tool.color}`}
                        >
                          <tool.icon className="h-8 w-8 text-white" />
                        </div>
                        <h3 className="text-xl font-bold text-foreground">
                          {tool.name}
                        </h3>
                        <p className="text-muted-foreground text-sm">
                          {tool.description}
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious className="hidden md:flex bg-white/90 hover:bg-white" />
            <CarouselNext className="hidden md:flex bg-white/90 hover:bg-white" />
          </Carousel>
        </div>
      </div>
    </section>
  );
};

// Contact Section
export const Contact = () => {
  const contactInfo = [
    {
      icon: Phone,
      title: "Teléfono",
      info: "+51 987 654 321",
      color: "from-education-orange to-education-yellow",
    },
    {
      icon: Mail,
      title: "Correo Electrónico",
      info: "info@ceama.edu.pe",
      color: "from-education-primary to-education-teal",
    },
    {
      icon: MapPin,
      title: "Dirección",
      info: "Av. Educación 123, Lima, Perú",
      color: "from-education-purple to-education-coral",
    },
    {
      icon: Clock,
      title: "Horario de Atención",
      info: "Lunes a Sábado: 8:00 AM - 8:00 PM",
      color: "from-education-teal to-education-secondary",
    },
  ];

  return (
    <section id="contacto" className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img
          src={contactBg}
          alt="Contacto background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-warm opacity-85"></div>
      </div>
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Contáctanos
          </h2>
          <p className="text-lg text-white/90 max-w-2xl mx-auto">
            Estamos aquí para responder todas tus preguntas y ayudarte a
            comenzar tu camino hacia el éxito académico
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {contactInfo.map((contact, index) => (
            <Card
              key={index}
              className="hover:shadow-xl transition-all duration-300 hover:scale-105 bg-white/95 backdrop-blur-sm"
            >
              <CardContent className="p-6 flex items-start space-x-4">
                <div
                  className={`flex-shrink-0 inline-flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br ${contact.color}`}
                >
                  <contact.icon className="h-7 w-7 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {contact.title}
                  </h3>
                  <p className="text-muted-foreground">{contact.info}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-12 text-center">
          <div className="inline-block bg-white/95 backdrop-blur-sm rounded-lg p-6 shadow-xl">
            <h3 className="text-xl font-bold text-foreground mb-2">
              ¿Listo para comenzar?
            </h3>
            <p className="text-muted-foreground">
              Contáctanos hoy mismo y únete a nuestra comunidad educativa
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};