import { useQuery } from "@tanstack/react-query";
import { messagesApi } from "@/lib/api";

interface UseMessagesParams {
  date_from?: string;
  date_to?: string;
  status?: string;
  keyword?: string;
  skip?: number;
  limit?: number;
}

export function useMessages(clientId: string, filters: UseMessagesParams = {}) {
  return useQuery({
    queryKey: ['messages', clientId, filters],
    queryFn: () => messagesApi.list(clientId, filters),
    enabled: !!clientId,
    keepPreviousData: true,
    staleTime: 30 * 1000, // 30 seconds
  });
}