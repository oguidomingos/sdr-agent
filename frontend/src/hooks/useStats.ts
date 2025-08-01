import { useQuery } from "@tanstack/react-query";
import { statsApi } from "@/lib/api";

interface UseStatsParams {
  date_from?: string;
  date_to?: string;
}

export function useStats(clientId: string, filters: UseStatsParams = {}) {
  return useQuery({
    queryKey: ['stats', clientId, filters],
    queryFn: () => statsApi.get(clientId, filters),
    enabled: !!clientId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}