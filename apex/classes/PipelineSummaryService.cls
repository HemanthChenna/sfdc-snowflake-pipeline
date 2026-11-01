/**
 * REST endpoint: GET /services/apexrest/pipeline-summary
 * Returns total open Opportunity amount by stage. Used by the data pipeline
 * to reconcile Snowflake against the Salesforce source of truth.
 */
@RestResource(urlMapping='/pipeline-summary/*')
global with sharing class PipelineSummaryService {

    global class StageSummary {
        public String stageName;
        public Integer openOpportunities;
        public Decimal totalAmount;
    }

    @HttpGet
    global static List<StageSummary> getSummary() {
        List<StageSummary> result = new List<StageSummary>();
        for (AggregateResult ar : [
            SELECT StageName stage, COUNT(Id) cnt, SUM(Amount) total
            FROM Opportunity
            WHERE IsClosed = false
            GROUP BY StageName
        ]) {
            StageSummary s = new StageSummary();
            s.stageName = (String) ar.get('stage');
            s.openOpportunities = (Integer) ar.get('cnt');
            s.totalAmount = (Decimal) ar.get('total');
            result.add(s);
        }
        return result;
    }
}
