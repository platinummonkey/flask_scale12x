// Person Model groovy functions test

// is-model
def get_older_30(element_type) {
    def get_persons_older = {
        return g.V('element_type', element_type).filter{it.age > 30};
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

    return transaction(get_persons_older);
}