import { useState } from 'react';

const Snow = () => {
    const [input, setInput] = useState('');

    return (
        <div className="h-screen w-screen bg-gradient-to-b from-black via-[#0a0a0a] to-[#1a1a1a] flex flex-col p-[10px]">
            <div className="w-full h-[120px] rounded-t-3xl backdrop-blur-md bg-white/10 border border-white/20 shadow-lg p-6 flex items-center">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Enter your input here..."
                    className="w-full px-4 py-3 rounded-xl bg-black/30 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400/50 focus:border-pink-400/50 transition-all"
                    style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                />
            </div>

            <div className="w-full flex-1 rounded-b-3xl backdrop-blur-md bg-white/10 border border-white/20 border-t-0 shadow-lg p-6">
                <div className='w-full h-full bg-gray-800 p-5 rounded-2xl fade-loading'>

                </div>
            </div>
        </div>
    );
};

export default Snow;