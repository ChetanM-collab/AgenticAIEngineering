import os
from crewai.tools import BaseTool


class WriteFileTool(BaseTool):
    """
    Tool to write text files under a restricted project directory.

    Usage from the agent:
      - Tool name: write_file
      - Args:
          path: relative path under {app_name}, e.g. "my-app/backend/src/Main.java"
          content: full file content as string
    """
    name: str = "write_file"
    description: str = (
        "Write a text file under the local project 'generated' directory. "
        "Takes a relative path (inside the generated folder) and file content."
    )

    # Your restricted base directory
    BASE_DIR: str = "/home/cmohite/projects/AgenticAIEngineering/generated1/"

    def _run(self, path: str, content: str) -> str:
        """
        :param path: Relative or sub-path under BASE_DIR (e.g. 'my-app/README.md')
        :param content: File content as a UTF-8 string
        :return: Confirmation message with the final absolute path
        """
        # If the agent passes a relative path like "my-app/README.md",
        # we join it to BASE_DIR
        # If they pass an absolute path, this still normalises & checks it.
        raw_path = path

        # Build an absolute path based on BASE_DIR + provided path
        abs_path = os.path.abspath(
            os.path.join(self.BASE_DIR, raw_path)
            if not os.path.isabs(raw_path)
            else raw_path
        )

        BASE_DIR = self.BASE_DIR

        # 🔒 Restrict writes to BASE_DIR only (your requested check)
        if not abs_path.startswith(BASE_DIR):
            raise PermissionError("Write restricted to project directory")

        # Ensure parent directories exist
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        # Write file
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"File written to {abs_path}"
