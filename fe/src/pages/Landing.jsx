import { useRef, useState } from 'react';
import ASCIIText from '../components/ASCIIText';
import { PuffLoader } from 'react-spinners';
import Antigravity from '../components/Antigravity';
import { useNavigate } from 'react-router-dom';
import PixelSnow from '../components/PixelSnow';

const Landing = () => {
    const containerRef = useRef(null);
    const navigate = useNavigate();
    const [isTransitioning, setIsTransitioning] = useState(false);
    const transitionStartedRef = useRef(false);

    const handleSpinnerClick = () => {
        if (containerRef.current && !transitionStartedRef.current) {
            transitionStartedRef.current = true;
            
            // Scroll to the container
            containerRef.current.scrollIntoView({ behavior: 'smooth' });
            
            // Detect when scroll completes by checking scroll position
            let scrollCheckInterval;
            let checkCount = 0;
            const maxChecks = 120; // Check for up to 3 seconds (60 * 50ms)
            
            const checkScrollComplete = () => {
                checkCount++;
                const containerTop = containerRef.current?.getBoundingClientRect().top || 0;
                const viewportHeight = window.innerHeight;
                
                // Check if container is near the top of viewport (within 150px)
                if (containerTop < viewportHeight * 0.2 + 150) {
                    clearInterval(scrollCheckInterval);
                    setIsTransitioning(true);
                    // Add a small delay for transition effect, then navigate
                    setTimeout(() => {
                        navigate('/Snow');
                    }, 500);
                } else if (checkCount >= maxChecks) {
                    // Fallback: if scroll takes too long, transition anyway
                    clearInterval(scrollCheckInterval);
                    setIsTransitioning(true);
                    setTimeout(() => {
                        navigate('/Snow');
                    }, 500);
                }
            };
            
            // Start checking after a short delay to allow scroll to begin
            setTimeout(() => {
                scrollCheckInterval = setInterval(checkScrollComplete, 50);
            }, 100);
        }
    };

    return (
        <>
            <div className={`transition-opacity duration-500 ${isTransitioning ? 'opacity-0' : 'opacity-100'}`}>
                <section className="w-screen h-screen relative overflow-x-hidden bg-black">
                    <img className="w-full h-screen absolute z-[0]" src="/aesthetic-snow.gif" alt="Aesthetic snow animation"/>
                    <div className="flex flex-col items-center justify-center h-screen">
                        <ASCIIText
                            text='Snowy Day'
                            textFontSize={35}
                            enableWaves={true}
                            asciiFontSize={4}
                        />
                    </div>
                    <div 
                        className="absolute bottom-8 left-1/2 transform -translate-x-1/2 cursor-pointer z-10 hover:scale-110 transition-transform duration-300"
                        onClick={handleSpinnerClick}
                    >
                        <PuffLoader color="white"/>
                    </div>
                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-b from-transparent via-black/50 to-black z-[1] pointer-events-none"></div>
                    <svg className="absolute bottom-0 left-0 w-full h-24 z-[2] pointer-events-none" viewBox="0 0 1200 120" preserveAspectRatio="none" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M0,120 Q300,80 600,100 T1200,100 L1200,120 L0,120 Z" fill="black" opacity="0.8"/>
                    </svg>
                </section>
                <section ref={containerRef} className="h-[80vh] w-screen relative overflow-hidden flex justify-center items-center pt-120 bg-gradient-to-b from-black via-[#0a0a0a] to-[#1a1a1a]">
                    <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-black to-transparent z-[1] pointer-events-none"></div>
                    <svg className="absolute top-0 left-0 w-full h-24 z-[2] pointer-events-none" viewBox="0 0 1200 120" preserveAspectRatio="none" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M0,0 Q300,40 600,20 T1200,20 L1200,0 L0,0 Z" fill="black" opacity="0.8"/>
                    </svg>

                    <div style={{ width: '100%', height: '1000x', position: 'relative' }}>
                    </div>
                    <PixelSnow
                    direction={90} />
                </section>
            </div>
        </>
    )
}

export default Landing;