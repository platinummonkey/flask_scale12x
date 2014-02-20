def get_persons_under_30() {
    def get_persons_younger = {
        return g.V('element_type', 'person').filter{it.age < 30};
    }

    def transaction = { final Closure closure ->
        try {
            results = closure();
            g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS);
            return results;
        } catch (e) {
            g.stopTransaction(TransactionalGraph.Conclusion.FAILURE);
            throw e;
        }
    }

    return transaction(get_persons_younger);
}