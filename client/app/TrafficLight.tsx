import clsx from 'clsx';

export default function TrafficLight({ color }: { color: 'R' | 'G' }) {
  return (
    <div className="flex justify-evenly items-center w-36 h-20 m-4 bg-black rounded-md">
      <div className={clsx('rounded-full w-10 h-10', { 'bg-green-500': color === 'G', 'bg-gray-500': color === 'R', })}></div>
      <div className={clsx('rounded-full w-10 h-10', { 'bg-red-500': color === 'R', 'bg-gray-500': color === 'G', })}></div>
    </div>
  );
}