export interface Materia {
    id_mat?: number;
    tipo: string;
    nome: string;
    nota: string;
    abc: string;
    status: string;
}
// {"tipo": "h", "nome": materia, "nota": nota, "abc": "D", "status": status}
// export interface Status {
//     status: false;
// }

// export type HistoricoOuParcial = Status | Materia[];