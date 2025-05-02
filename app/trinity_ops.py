
import os
import subprocess
import shutil
import datetime
from .utils import run_shell_command, file_size_in_megabytes
from .database import SessionLocal, AssemblyJob

TRINITY_PATH = "/home/jcap/trinityrnaseq/Trinity"  # Update to your real path
TRINITY_STATS = "TrinityStats.pl"  # Assumes it's in PATH or Trinity dir


def estimate_assembly_time(left, right, cpu, speed_per_core=50):
    size_left = file_size_in_megabytes(left)
    size_right = file_size_in_megabytes(right)
    total_size = size_left + size_right
    estimated_minutes = total_size / (speed_per_core * cpu)
    return max(1, round(estimated_minutes))


def run_trinity_job(job_id, left, right, output_dir, max_memory, cpu):
    db = SessionLocal()
    job = db.query(AssemblyJob).filter(AssemblyJob.id == job_id).first()

    try:
        job.status = "running"
        job.start_time = datetime.datetime.utcnow()
        db.commit()

        os.makedirs(output_dir, exist_ok=True)

        command = [
            TRINITY_PATH,
            "--seqType", "fq",
            "--max_memory", max_memory,
            "--left", left,
            "--right", right,
            "--CPU", str(cpu),
            "--output", output_dir
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        job.log = result.stdout

        fasta_path = os.path.join(output_dir, "Trinity.fasta")
        if result.returncode == 0 and os.path.exists(fasta_path):
            job.status = "completed"
        else:
            job.status = "failed"

        job.end_time = datetime.datetime.utcnow()
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.log = str(e)
        job.end_time = datetime.datetime.utcnow()
        db.commit()
    finally:
        db.close()


def get_trinity_stats(output_dir):
    fasta_path = os.path.join(output_dir, "Trinity.fasta")
    if not os.path.exists(fasta_path):
        return "Trinity.fasta not found."

    command = f"{TRINITY_STATS} {fasta_path}"
    stats = run_shell_command(command)
    return stats
