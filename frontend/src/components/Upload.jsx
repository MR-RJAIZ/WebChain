import { useRef, useState } from "react";
import { Upload, FileArchive, CheckCircle2, X } from "lucide-react";

function UploadProject() {
    const fileInputRef = useRef(null);

    const [file, setFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);

    const handleFile = (selectedFile) => {
        if (!selectedFile) return;
        setFile(selectedFile);
    };

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        handleFile(selectedFile);
    };

    const handleDrop = (event) => {
        event.preventDefault();
        setIsDragging(false);

        const droppedFile = event.dataTransfer.files[0];
        handleFile(droppedFile);
    };

    const removeFile = () => {
        setFile(null);

        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    return (
        <div className="mx-auto w-full max-w-2xl">

            {!file && (
                <div
                    onDragOver={(event) => {
                        event.preventDefault();
                        setIsDragging(true);
                    }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition ${isDragging
                            ? "border-cyan-400 bg-cyan-400/10"
                            : "border-white/20 bg-white/[0.03] hover:border-cyan-400/50 hover:bg-white/[0.05]"
                        }`}
                >
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-400">
                        <Upload size={30} />
                    </div>

                    <h3 className="mt-5 text-xl font-bold">
                        Upload your website
                    </h3>

                    <p className="mt-2 text-gray-400">
                        Drag & drop your project here
                    </p>

                    <p className="mt-2 text-sm text-gray-500">
                        or click to browse files
                    </p>

                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        onChange={handleFileChange}
                    />

                    <div className="mt-6 flex flex-wrap justify-center gap-2 text-xs text-gray-500">
                        <span className="rounded-lg bg-white/5 px-3 py-2">
                            HTML
                        </span>

                        <span className="rounded-lg bg-white/5 px-3 py-2">
                            CSS
                        </span>

                        <span className="rounded-lg bg-white/5 px-3 py-2">
                            JavaScript
                        </span>

                        <span className="rounded-lg bg-white/5 px-3 py-2">
                            React
                        </span>
                    </div>
                </div>
            )}

            {file && (
                <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-6">

                    <div className="flex items-center justify-between">

                        <div className="flex items-center gap-4">

                            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                                <FileArchive size={25} />
                            </div>

                            <div className="text-left">
                                <p className="max-w-[220px] truncate font-semibold">
                                    {file.name}
                                </p>

                                <p className="text-sm text-gray-400">
                                    {(file.size / 1024).toFixed(2)} KB
                                </p>
                            </div>

                        </div>

                        <button
                            onClick={removeFile}
                            className="rounded-lg p-2 text-gray-400 transition hover:bg-red-400/10 hover:text-red-400"
                        >
                            <X size={20} />
                        </button>

                    </div>

                    <div className="mt-5 flex items-center gap-2 text-sm text-green-400">
                        <CheckCircle2 size={18} />
                        Project selected successfully
                    </div>

                    <button
                        onClick={() => alert("Deployment feature coming next!")}
                        className="mt-6 w-full rounded-xl bg-cyan-400 py-3 font-bold text-black transition hover:scale-[1.02] hover:bg-cyan-300"
                    >
                        Deploy Project
                    </button>

                </div>
            )}
        </div>
    );
}

export default UploadProject;