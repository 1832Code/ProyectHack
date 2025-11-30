import SkeletonLoader from "./skeleton-sloader";
import CodeStreaming from "./code-streaming";
import "../../../styles/ClaimLoading.css";

export default function ClaimLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header elegante con el capibara */}
        <div className="flex flex-col items-center mb-8 md:mb-12">
          <div className="relative mb-6">
            <div className="capybaraloader">
              <div className="capybara scale-75 md:scale-100">
                <div className="capyhead">
                  <div className="capyear">
                    <div className="capyear2"></div>
                  </div>
                  <div className="capyear"></div>
                  <div className="capymouth">
                    <div className="capylips"></div>
                    <div className="capylips"></div>
                  </div>
                  <div className="capyeye"></div>
                  <div className="capyeye"></div>
                </div>
                <div className="capyleg"></div>
                <div className="capyleg2"></div>
                <div className="capyleg2"></div>
                <div className="capy"></div>
              </div>
              <div className="loader">
                <div className="loaderline"></div>
              </div>
            </div>
          </div>

          {/* Título elegante */}
          <div className="text-center">
            <h1 className="text-2xl md:text-4xl font-light text-white mb-2">
              Procesando tu solicitud
            </h1>
            <p className="text-slate-300 text-sm md:text-base font-light">
              Estamos preparando todo para ti...
            </p>
          </div>
        </div>

        {/* Contenido principal en grid responsivo */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 max-w-6xl mx-auto">
          {/* Skeleton Loader Card */}
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10 shadow-2xl hover:shadow-purple-500/10 transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-3 h-3 bg-purple-400 rounded-full mr-2"></div>
              <h3 className="text-white font-medium text-lg">Cargando datos</h3>
            </div>
            <SkeletonLoader />
          </div>

          {/* Code Streaming Card */}
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10 shadow-2xl hover:shadow-blue-500/10 transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-3 h-3 bg-blue-400 rounded-full mr-2"></div>
              <h3 className="text-white font-medium text-lg">
                Generando código
              </h3>
            </div>
            <CodeStreaming />
          </div>
        </div>

        {/* Progress bar sutil en mobile */}
        <div className="fixed bottom-0 left-0 right-0 md:hidden">
          <div className="bg-slate-800/50 backdrop-blur-sm p-4">
            <div className="w-full bg-slate-700 rounded-full h-1.5"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
