@IsTest
private class PipelineSummaryServiceTest {

    @TestSetup
    static void setup() {
        Account a = new Account(Name = 'Test Account');
        insert a;
        insert new List<Opportunity>{
            new Opportunity(Name = 'O1', AccountId = a.Id, StageName = 'Prospecting',
                            Amount = 1000, CloseDate = Date.today().addDays(30)),
            new Opportunity(Name = 'O2', AccountId = a.Id, StageName = 'Prospecting',
                            Amount = 500,  CloseDate = Date.today().addDays(30)),
            new Opportunity(Name = 'O3', AccountId = a.Id, StageName = 'Closed Won',
                            Amount = 9999, CloseDate = Date.today())
        };
    }

    @IsTest
    static void returnsOnlyOpenOpportunitiesGroupedByStage() {
        Test.startTest();
        List<PipelineSummaryService.StageSummary> out = PipelineSummaryService.getSummary();
        Test.stopTest();

        System.assertEquals(1, out.size(), 'Closed stages must be excluded');
        System.assertEquals('Prospecting', out[0].stageName);
        System.assertEquals(2, out[0].openOpportunities);
        System.assertEquals(1500, out[0].totalAmount);
    }
}
