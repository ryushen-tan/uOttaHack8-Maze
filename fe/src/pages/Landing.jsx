import { useRef } from 'react';
import ASCIIText from '../components/ASCIIText';
import { PuffLoader } from 'react-spinners';
import Antigravity from '../components/Antigravity';
import Crosshair from '../components/Crosshair';
import { Link } from 'react-router-dom';

const Landing = () => {
    const containerRef = useRef(null);

    const handleSpinnerClick = () => {
        if (containerRef.current) {
            containerRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <>
            <section className="w-screen h-screen relative overflow-x-hidden bg-black">
                <img className="w-full h-screen absolute z-[0]" src="/aesthetic-snow.gif" alt="Aesthetic snow animation"/>
                <div className="flex flex-col items-center justify-center h-screen">
                    <ASCIIText
                        text='Maze'
                        textFontSize={50}
                        enableWaves={true}
                        asciiFontSize={4}
                    />
                </div>
                <div 
                    className="absolute bottom-8 left-1/2 transform -translate-x-1/2 cursor-pointer z-10"
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
            <Antigravity
                color="#ffffff"
            />
            </div>
  
                
                <div className="w-2xl absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
                    <h1 className="w-full" style={{ fontFamily: 'Rubik Pixels, sans-serif' }}>
                        <Link to="/maze" className="flex items-center justify-center transition-transform duration-300 ease-in-out hover:scale-110">
                            {'Enter the Maze'.split('').map((char, index) => (
                                <span
                                    key={index}
                                    className="inline-block shuffle-letter text-[150px] text-gray-600 font-semibold hover:cursor-pointer hover:text-white"
                                    style={{
                                        animationDelay: `${index * 0.1}s`
                                    }}
                                >
                                    {char === ' ' ? '\u00A0' : char}
                                </span>
                            ))}
                        </Link>
                    </h1>
                </div>
                <Crosshair containerRef={containerRef} color='#2b2b2b'/>
            </section>
        </>
    )
}

export default Landing;