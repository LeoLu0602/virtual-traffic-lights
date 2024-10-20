'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import TrafficLight from './TrafficLight';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? '';
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export default function Home() {
  const [trafficLight1, setTrafficLight1] = useState<'R' | 'G'>('R');
  const [trafficLight2, setTrafficLight2] = useState<'R' | 'G'>('R');
  const [traffic1, setTraffic1] = useState<number>(0);
  const [traffic2, setTraffic2] = useState<number>(0);

  useEffect(() => {
    const channel = supabase.channel('channel')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'intersection', filter: 'id=eq.1', },
        (payload) => {
          if (payload.new) {
            setTrafficLight1(payload.new.traffic_light1);
            setTrafficLight2(payload.new.traffic_light2);
            setTraffic1(payload.new.traffic1.toFixed(2));
            setTraffic2(payload.new.traffic2.toFixed(2));
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <>
      <main className='flex flex-col justify-center items-center h-screen font-bold bg-gray-200'>
        <h1 className='mb-8 text-2xl'>Virtual Traffic Lights for Self-Driving Cars</h1>
        <h2 className='mb-8 text-xl text-sky-500'>The vehicle is approaching intersection #1</h2>
        <section>
          <h2 className='text-center'>Traffic: {traffic1}</h2>
          <TrafficLight color={trafficLight1} />
          <h2 className='text-center'>Traffic: {traffic2}</h2>
          <TrafficLight color={trafficLight2} />
        </section>
      </main>
    </>
  );
}