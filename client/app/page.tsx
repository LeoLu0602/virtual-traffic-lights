'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import clsx from 'clsx';
import TrafficLight from './TrafficLight';
import Alert from './Alert';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? '';
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export default function Home() {
  const [trafficLight1, setTrafficLight1] = useState<'R' | 'G'>('R');
  const [trafficLight2, setTrafficLight2] = useState<'R' | 'G'>('R');
  const [traffic1, setTraffic1] = useState<number>(0);
  const [traffic2, setTraffic2] = useState<number>(0);
  const [earthquakeAlert, setEarthquakeAlert] = useState<string>('');
  const heavier: 0 | 1 | 2 =
    traffic1 === traffic2 ? 0 : traffic1 > traffic2 ? 1 : 2;

  useEffect(() => {
    const channel = supabase
      .channel('channel')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'intersection',
          filter: 'id=eq.1',
        },
        (payload: {
          new: {
            traffic_light1: 'R' | 'G';
            traffic_light2: 'R' | 'G';
            traffic1: number;
            traffic2: number;
            earthquake_alert: string;
          };
        }) => {
          if (payload.new) {
            setTrafficLight1(payload.new.traffic_light1);
            setTrafficLight2(payload.new.traffic_light2);
            setTraffic1(payload.new.traffic1);
            setTraffic2(payload.new.traffic2);
            setEarthquakeAlert(payload.new.earthquake_alert);
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <>
      <main className="flex flex-col justify-center items-center h-screen font-bold bg-gray-100">
        <h1 className="mb-8 text-3xl">
          Virtual Traffic Lights for Self-Driving Cars
        </h1>
        <h2 className="mb-8 text-xl">
          The vehicle is approaching intersection #1
        </h2>
        <h2 className="text-center">
          Your direction's traffic: <span className={clsx({'text-red-500': heavier === 1})}>{traffic1.toFixed(2)}</span>
        </h2>
        <TrafficLight color={trafficLight1} />
        <h2 className="text-center">
          The other direction's traffic: <span className={clsx({'text-red-500': heavier === 2})}>{traffic2.toFixed(2)}</span>
        </h2>
        <TrafficLight color={trafficLight2} />
        <Alert msg={earthquakeAlert} />
      </main>
    </>
  );
}
