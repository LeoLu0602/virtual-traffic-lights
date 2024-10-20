export default function Alert({ msg }: { msg: string }) {
  if (msg === '') {
    return <></>;
  }

  return (
    <div className="fixed left-0 bottom-0 w-72 flex-wrap bg-red-500 m-1 p-4 rounded-md animate-fadeIn">
      {msg}
    </div>
  );
}
