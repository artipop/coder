import { useState, useEffect } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
} from "@/components/ui/pagination";

export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState({});
  const [nextPageToken, setNextPageToken] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const pageSize = 10; // Количество документов на странице

  // Функция загрузки данных
  async function loadDocuments(token = null) {
    setIsLoading(true);
    try {
      const queryParams = new URLSearchParams({
        ...(token ? { pageToken: token } : {}),
        pageSize: pageSize.toString(),
      });

      const response = await fetch(`/gdocs?${queryParams.toString()}`);
      if (!response.ok) {
        console.error("Ошибка загрузки данных:", response.statusText);
        setIsLoading(false);
        return;
      }
      const data = await response.json();

      setDocuments((prev) => [...prev, ...data.documents]); // Добавляем новые документы
      setNextPageToken(data.nextPageToken || null);
    } catch (error) {
      console.error("Ошибка соединения:", error);
    } finally {
      setIsLoading(false);
    }
  }

  // Обработчик состояния чекбоксов
  const handleCheckboxChange = (docId, checked) => {
    setSelectedDocuments((prev) => ({
      ...prev,
      [docId]: checked,
    }));
  };

  // Отправка данных на сервер
  async function sendDocuments() {
    const formattedData = documents.map((doc) => ({
      id: doc.id,
      is_checked: selectedDocuments[doc.id] || false,
    }));

    try {
      const response = await fetch("/gdocs/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formattedData),
      });

      if (!response.ok) {
        console.error("Ошибка отправки данных:", response.statusText);
        alert("Ошибка при отправке данных.");
        return;
      }

      alert("Данные успешно отправлены.");
    } catch (error) {
      console.error("Ошибка при запросе:", error);
      alert("Ошибка соединения.");
    }
  }

  // Первичная загрузка данных
  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="p-4 flex flex-col gap-4">
      <div>
        {documents.map((doc) => (
          <div key={doc.id} className="flex items-center gap-4">
            <Checkbox
              id={`checkbox-${doc.id}`}
              checked={selectedDocuments[doc.id] || false}
              onCheckedChange={(checked) => handleCheckboxChange(doc.id, checked)}
            />
            <a href={doc.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
              {doc.name}
            </a>
          </div>
        ))}
      </div>
      <Pagination>
        <PaginationContent>
          {nextPageToken && (
            <PaginationItem>
              <PaginationLink
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  loadDocuments(nextPageToken);
                }}
              >
                Загрузить следующую страницу
              </PaginationLink>
            </PaginationItem>
          )}
        </PaginationContent>
      </Pagination>
      <Button id="send-documents" onClick={sendDocuments}>
        Отправить выбранные документы
      </Button>
    </div>
  );
}
