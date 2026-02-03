import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";

export default function DocumentList() {
    async function sendDocuments() {
        try {
            const response = await fetch("/gdocs/save", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ documents: props.documents }),
            });

            if (!response.ok) {
                console.error("Ошибка при запросе к API:", response.statusText);
                // TODO
                // alert("Ошибка при отправке данных.");
                return;
            }

            const data = await response.json();
            console.log("Результат API:", data);
            // TODO
            // alert("Данные успешно отправлены.");
        } catch (error) {
            console.error("Ошибка при запросе к API:", error);
            // TODO
            // alert("Ошибка соединения.");
        }
    }

    return (
        <div id="document-list" className="p-4 flex flex-col gap-4">
            {props.documents.map((doc, index) => (
                <div key={index} className="flex items-center gap-4">
                    <Checkbox
                        id={`checkbox-${index}`}
                        checked={doc.checked}
                        onCheckedChange={(checked) => {
                            const updatedDocs = [...props.documents];
                            updatedDocs[index].checked = checked;
                            updateElement(Object.assign(props, { documents: updatedDocs }));
                        }}
                    />
                    <a href={doc.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                        {doc.name}
                    </a>
                </div>
            ))}
            <Button id="send-documents" onClick={sendDocuments}>
                Отправить выбранные документы
            </Button>
        </div>
    );
}
